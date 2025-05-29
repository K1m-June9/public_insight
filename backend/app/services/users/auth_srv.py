from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from jose import jwt, JWTError, ExpiredSignatureError
import logging

# 커스텀 모듈
from app.core.config import settings
from app.core.security import verify_password

from app.schemas.oauth2_sch import sch_login_request
from app.repositories.users.oauth2_repo import repo_id_get, repo_device_get_or_create, repo_refresh_token_update_or_create, repo_refresh_token_delete, repo_refresh_token_get_by_device, repo_refresh_token_get_by_token, repo_use_refresh_token, repo_device_get
from app.utils.oauth2.jwt_utils import utils_create_refresh_token, utils_create_access_token, utils_decode_token
from app.utils.oauth2.jwt_redis import utils_access_token_blacklist, utils_is_refresh_token_used, utils_mark_refresh_token_used
from app.utils.oauth2.token_utils import utils_create_token_response

logger = logging.getLogger(__name__)

"""
Access Token 
    - Redis 저장
    - 사용자가 인증된 상태임을 증명하고, 보호된 API나 리소스에 접근할 때 사용

Refresh Token
    - DB 저장
    - Access Token이 만료됐을 때 새로운 Access Token을 발급받기 위한 토큰
"""

# 로그인
async def srv_login_user(request: Request, login_req: sch_login_request, db:AsyncSession):
    # 1. 로그인 체크
    user = await repo_id_get(login_req.username, db)
    if not user or not verify_password(login_req.password, user.password_hash):
        logger.warning(f"Login failed for user: {login_req.username}")
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")


    # 2. Refresh Token 준비물
    # 사용자 디바이스 정보 가져오기
    device_name = request.headers.get("User-Agent", "Unknown Device")
    logger.info(f"Device info: username={user.username}, device_name: {device_name}")


    # User ID + device name로 device_info 정보 저장
    # device id : 디바이스 고유 ID(PK)
    # device name : 디바이스 이름
    device = await repo_device_get_or_create(user.username, device_name, db)
    logger.info(f"Device info: {device.device_id}")


    # 3. Refresh Token 생성
    refresh_token = await utils_create_refresh_token()
    expires_at = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


    # 4. Refresh Token DB에 저장
    await repo_refresh_token_update_or_create(device.device_id, refresh_token, expires_at, db)
    logger.info(f"Refresh token created for device_id: {device.device_id}, expires_at: {expires_at}")


    # 5. Access Token 생성
    # Refresh Token에서 생성한 device_id 사용
    access_token = await utils_create_access_token(
        {"sub":str(user.username), "device_id":str(device.device_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.info(f"Access token created for user: {user.username}")


    # 6. 응답 반환 만들기
    # Access Token : Json
    # refresh Token : HttpOnly
    response = await utils_create_token_response(access_token, refresh_token)
    logger.info(f"Login success for user: {user.username}")

    # 7. 반환
    return response 


# 로그아웃
async def srv_logout_user(access_token:str, db: AsyncSession):
    try:
        logger.info("Logout attempt")

        # 1. Access Token 디코딩
        payload = await utils_decode_token(access_token)
        username = payload.get("sub")
        device_id = payload.get("device_id")
        jti = payload.get("jti")

        if not username or not device_id or not jti:
            logger.error("Invalid token payload: missing username/device_id/jti")
            raise HTTPException(status_code=401, detail="Invalid token")

        # 2. 다중 디바이스 관리 및 블랙리스트 등록
        await utils_access_token_blacklist(username, device_id, jti)

        # 3. Refresh Token 가져오기
        token_obj = await repo_refresh_token_get_by_device(device_id, db)

        # 3. Refresh Token 삭제
        deleted = await repo_refresh_token_delete(device_id, db)
        if deleted:
            await utils_mark_refresh_token_used(token_obj.refresh_token)

        logger.info(f"Logout success for user={username}, device_id={device_id}")
    except Exception as e:
        logger.exception(f"Logout error: {e}")
        raise


# Refresh
async def srv_refresh(request:Request, db:AsyncSession):
    try:
        logger.info("Refresh token request received")

        # 1. 쿠키에서 refresh_token 추출
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            logger.warning("Missing refresh token in request cookies")
            raise HTTPException(status_code=401, detail="Missing refresh token")
    

        # 2. Redis에서 재사용된 Refresh Token인지 확인(재사용 방지)
        if await utils_is_refresh_token_used(refresh_token):
            logger.warning("Attempt to reuse refresh token detected")
            raise HTTPException(status_code=403, detail="Used refresh token")
    

        # 3. DB에서 Refresh Token 유효성 확인
        token_obj = await repo_refresh_token_get_by_token(refresh_token, db)
        if not token_obj or token_obj.expires_at < datetime.now():
            logger.warning("Invalid or expired refresh token")
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    

        # 4. username 조회 (device_id 기준)
        user = await repo_device_get(token_obj.device_id, db)
        if not user:
            logger.error(f"Device user not found for device_id={token_obj.device_id}")
            raise HTTPException(status_code=404, detail="Device user not found")
    

        # 5. 기존 Refresh Token 사용 처리(삭제 + Redis 기록)
        await repo_use_refresh_token(refresh_token, db)
        await utils_mark_refresh_token_used(refresh_token)
        logger.info(f"Used refresh token processed for device_id={token_obj.device_id}")


        # 6. 새로운 Access Token 생성
        # 기존 가지고 있던 Refresh Token을 통해 Access Token 재발급
        new_access_token = await utils_create_access_token(
        {"sub":str(user.username), "device_id":str(token_obj.device_id)},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))


        # 7. 새로운 Refresh Token 발급
        new_refresh_token = await utils_create_refresh_token()
        new_exp = datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)


        # 8. DB에 새로운 Refresh Token 저장
        await repo_refresh_token_update_or_create(token_obj.device_id, new_refresh_token, 
        new_exp, db)
        logger.info(f"New tokens issued for user={user.username}, device_id={token_obj.device_id}")


        # 9. 응답
        # Access Token : Json
        # refresh Token : HttpOnly
        response = await utils_create_token_response(new_access_token, new_refresh_token)
        logger.info("Token refresh success")

        return response
    
    except Exception as e:
        logger.error(f"Error in srv_refresh: {e}", exc_info=True)
        await db.rollback()  # Rollback any changes in case of error
        raise HTTPException(status_code=500, detail="Internal Server Error")
