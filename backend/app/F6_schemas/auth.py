from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

from app.F6_schemas import base
from app.F7_models.users import UserRole, UserStatus

# =================================
# 1. 로그인 스키마
# =================================
class LoginRequest(BaseModel):
    """로그인 스키마"""
    user_id: str
    password: str


# =================================
# 2. 로그아웃 스키마
# =================================
class LogoutRequest(BaseModel):
    """로그아웃 스키마"""
    refresh_token: str
    device_id: str  


# =================================
# 3. Access Token 관련 스키마
# =================================
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


# =================================
# 4. 회원가입 관련 스키마
# =================================
class UserCreate(BaseModel):
    user_id: str = Field(min_length=8, max_length=20)
    email: EmailStr
    password: str = Field(min_length=10, max_length=25)
    nickname: Optional[str] = None 
    terms_agreed: bool
    privacy_agreed: bool
    notification_agreed: Optional[bool] = False


class UserResponse(base.BaseSchema):
    id: int
    user_id: str
    email: EmailStr
    nickname: str
    role: UserRole
    status: UserStatus
    terms_agreed: bool
    privacy_agreed: bool
    notification_agreed: bool
    terms_agreed_at: Optional[datetime]
    privacy_agreed_at: Optional[datetime]
    marketing_agreed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class RegisterSuccessResponse(base.SuccessResponse):
    message: str = "회원가입이 완료되었습니다"



# =================================
# 5. 중복 및 규칙 검사 관련 스키마
# =================================
class UserCheckID(BaseModel):
    user_id: str


# find-id에도 사용
class UserCheckEmail(BaseModel):
    email: EmailStr


# =================================
# 6. 이메일 인증 관련 스키마
# =================================

class EmailVerifyCode(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)


class EmailSendSuccessResponse(base.SuccessResponse):
    message: str = "인증코드가 전송되었습니다"


class EmailVerifySuccessResponse(base.SuccessResponse):
    message: str = "인증이 완료되었습니다"


# =================================
# 7. 아이디 찾기 및 비밀번호 찾기 관련 스키마
# =================================

class FindIdResponse(base.SuccessResponse):
    masked_user_id: str


class ResetPasswordRequest(BaseModel):
    user_id: str = Field(min_length=1)  
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str


class PasswordResetEmailSentResponse(base.SuccessResponse):
    message: str


class TokenVerificationResponse(BaseModel):
    valid: bool
    email: EmailStr
    user_id: str
    message: str

class PasswordResetCompleteResponse(base.BaseResponse):
    message: str 

class PasswordResetSubmitRequest(base.SuccessResponse):
    token: str = Field
    new_password: str = Field(min_length=10, max_length=25)