from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

from app.F6_schemas import base
from app.F7_models.users import UserRole

# ============================================================================
# 1. 로그인 스키마
# ============================================================================
class LoginRequest(BaseModel):
    """로그인 스키마"""
    user_id: str
    password: str

# ============================================================================
# 2. 로그아웃 스키마
# ============================================================================
class LogoutRequest(BaseModel):
    """로그아웃 스키마"""
    refresh_token: str
    device_id: str  


# ============================================================================
# 3. Access Token 관련 스키마
# ============================================================================
class TokenPayload(BaseModel):
    jti: Optional[str]
    user_id: str 
    role: Optional[UserRole]
    exp: Optional[datetime]
    iat: Optional[datetime]
    tpe: Optional[str]

class TokenData(BaseModel):
    """Access Token 정보"""
    access_token: str #인코딩된 JWT 문자열
    token_type: str 
    expires_in: int
    refresh_token: Optional[str] = None  # 앱용 응답: 새 Refresh Token 포함

class TokenResponse(base.SuccessResponse):
    message: str
    data: TokenData


