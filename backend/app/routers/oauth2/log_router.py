from fastapi import APIRouter, HTTPException, Request, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError

# 커스텀 모듈
from app.schemas.oauth2_sch import sch_access_token, sch_login_request
from app.database.get_db import get_db
from app.services.users.auth_srv import srv_login_user, srv_logout_user, srv_refresh
from app.utils.oauth2.jwt_utils import oauth2_scheme
from app.utils.oauth2.token_utils import utils_check_access_token

router = APIRouter(tags=["Auth"])


"""
Access Token 
    - Redis 저장
    - 사용자가 인증된 상태임을 증명하고, 보호된 API나 리소스에 접근할 때 사용
    - 전달 : JSON으로 body에 넣어서 전달

Refresh Token
    - DB 저장
    - Access Token이 만료됐을 때 새로운 Access Token을 발급받기 위한 토큰
    - 보안상 매우 중요하기에 httponly 쿠키로 전달
"""

# 로그인
# response
# Access Token : Json
# refresh Token : HttpOnly
@router.post("/login")
async def router_login(request: Request, login_req: sch_login_request, db:AsyncSession = Depends(get_db)):
    try:
        response = await srv_login_user(request, login_req, db)
        return response
    except HTTPException as e:
        raise e  
    except Exception as e:
        print(f"signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 로그아웃
@router.post("/logout", status_code=200)
async def router_logout(access_token:str = Depends(oauth2_scheme), db:AsyncSession = Depends(get_db)):
    try:
        await srv_logout_user(access_token, db)
        return Response(status_code=200)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


#Refresh Token 재발급
#사용목적: Access Token이 만료된 경우, 사용자는 Refresh Token을 이용해서 새로운 Access Token과 Refresh Token을 재발급받기 위함
@router.post("/refresh", response_model=sch_access_token)
async def router_refresh(request: Request,db:AsyncSession = Depends(get_db)):
    try:
        response = await srv_refresh(request, db)
        return response
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 인증이 필요한 API 접근 시 사용
# 사용목적: 로그인 후 발급받은 Access Token이 유효한지를 검증
@router.post("/protected")
async def router_protected(token: str = Depends(oauth2_scheme)):
    payload = await utils_check_access_token(token)
    return {
        "message": f"Hello user {payload.get('sub')} from device {payload.get('device_id')}"
        }


