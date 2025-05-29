from pydantic import BaseModel, EmailStr, Field

###수정###
# 회원가입
class sch_user_signup(BaseModel):
    username: str = Field(..., min_length=8, max_length=12) # ID
    nickname: str = Field(..., min_length=2, max_length=20) # 닉네임
    password: str = Field(..., min_length=8, max_length=32) # 비밀번호
    email: EmailStr # 이메일
    notification: bool # 알림 동의
    advertising_consent: bool # 광고 동의
    class Config:
        from_attributes = True