from pydantic import BaseModel, Field

# 이메일 인증
class sch_email_verify_code(BaseModel):
    email: str
    code: str = Field(..., min_length=6, max_length=6)