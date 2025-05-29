from fastapi import HTTPException, Response
from fastapi.responses import JSONResponse
from jose import JWTError, ExpiredSignatureError

# 커스텀 모듈
from app.core.config import settings
from app.utils.oauth2.jwt_utils import utils_decode_token
from app.utils.oauth2.jwt_redis import utils_is_access_token_blacklisted

# JWT Access Token을 검증하여 인증된 사용자만 접근할 수 있도록 보호된 API
# 사용목적: 로그인 후 발급받은 Access Token이 유효한지를 검증해서
# 유효하면 -> 리소스 제공
# 유효하지 않으면 (블랙리스트(로그아웃/만료된 토큰)) -> 접근 차단
async def utils_check_access_token(token:str):
    try:
        # 1. 토큰 디코딩
        payload = await utils_decode_token(token)
        username = payload.get("sub")
        device_id = payload.get("device_id")
        jti = payload.get("jti")
        if not all([username, device_id, jti]):
            raise HTTPException(status_code=400, detail="Token missing required claims")

        # 2. 해당 토큰 블랙리스트 체크
        if await utils_is_access_token_blacklisted(username, device_id, jti):
            raise HTTPException(status_code=401, detail="Token is blacklisted")
        
        # 3. 반환 
        return payload 
    
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def utils_create_token_response(access_token:str, refresh_token:str)->Response:
    response = JSONResponse(content={"access_token":access_token})
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax" if settings.IS_LOCAL else "strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    return response