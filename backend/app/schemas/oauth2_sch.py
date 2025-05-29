from pydantic import BaseModel, Field
from typing import Optional

# 로그인 및 갱신 (사용자에게 전달)
class sch_access_token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 로그인 정보
class sch_login_request(BaseModel):
    username: str = Field(..., min_length=8, max_length=12) # ID
    password: str = Field(..., min_length=8, max_length=32) # 비밀번호

