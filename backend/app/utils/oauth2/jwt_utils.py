from datetime import datetime, timedelta
from jose import jwt, JWTError
import uuid 
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException

# 커스텀 모듈
from app.core.config import settings

# Authorization 헤더에서 Bearer 토큰 추출 - access_token 들어있음
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# JWT Access Token 생성
# username, device_id, exp, iat, jti
async def utils_create_access_token(data: dict, expires_delta: timedelta=None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    # JWT의 유효기간(exp), 발행시간(iat), 고유 식별자(jti) : 필수 보안 요소
    to_encode.update({
        "exp":int(expire.timestamp()),
        "iat":int(datetime.now().timestamp()),
        "jti":str(uuid.uuid4())
    })

    encode_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encode_jwt

# Access Token 디코딩
async def utils_decode_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid JWT token")


# Refresh Token 생성
async def utils_create_refresh_token():
    return str (uuid.uuid4())


