from fastapi import APIRouter, HTTPException, Request, Depends

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

# 커스텀 모듈
from app.database.get_db import get_db
from app.schemas.email_sch import sch_email_verify_code

from app.repositories.check.duplicate_check_repo import repo_email_exists
from app.utils.email.email_send_utils import utils_email_send_code
from app.utils.email.email_redis_utils import utils_email_verify

router = APIRouter(tags=["Users"])


#벤된 이메일인지 확인
#이메일 인증코드 발송 
# 통과 시 True를 반환
# 회원가입 버튼 클릭시 반환한 True를 확인
@router.post("/email/code/send")
async def router_email_check(email: str, db:AsyncSession = Depends(get_db))->Union[bool, dict]:
    # 중복 체크
    if not await repo_email_exists(db, email):
        raise HTTPException(status_code=400, detail="중복 사용된 이메일 입니다.")

    # 인증 번호 전송
    await utils_email_send_code(email)
    return {"is_available": True, "message": "인증 번호가 전송되었습니다."}


# 이메일 인증 코드 검증
# 통과 시 True를 반환
# 회원가입 버튼 클릭시 반환한 True를 확인
# 실패시 프론트에서는 제대로 입력해달라는 말 + 인증 코드 재발송 버튼
@router.post("/email/code/verify")
async def router_email_verify(valid: sch_email_verify_code)->Union[bool, dict]:
    is_valid = await utils_email_verify(valid.email, valid.code)
    if not is_valid:
        raise HTTPException(status_code=400, detail="인증 코드가 올바르지 않습니다.") 
    return {"is_valid": True, "message": "인증이 완료되었습니다."}
