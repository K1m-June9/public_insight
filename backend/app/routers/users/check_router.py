from fastapi import APIRouter, HTTPException, Request, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

# 커스텀 모듈
from app.database.get_db import get_db
from app.repositories.check.duplicate_check_repo import repo_id_exists , repo_nickname_exists
from app.repositories.check.ban_check_repo import repo_nickname_banned_keywords
from app.utils.users.check_utils import utils_id_rule, utils_id_banned_keywords, utils_nickname_rule, utils_password_rule


router = APIRouter(tags=["Users"])


# 사용자가 ID 입력 후 확인 버튼 클릭시 동작
# User ID 규칙, 금칙어, 중복 체크
# 통과 시 True를 반환 
@router.post("/check/id")
async def router_id_check(user_id: str, db:AsyncSession = Depends(get_db))-> Union[bool, dict]:
    # 규칙 체크
    if not utils_id_rule(user_id):
        raise HTTPException(status_code=400, detail="규칙으로 사용 불가한 ID 입니다.")
    
    # 금칙어 체크
    if not await utils_id_banned_keywords(db, user_id):
        raise HTTPException(status_code=400, detail="금칙어로 사용 불가한 단어입니다.")

    # 중복 체크
    if not await repo_id_exists(db, user_id):
        raise HTTPException(status_code=400, detail="이미 사용 중인 ID입니다.")
    
    return {"success": True, "message": "사용 가능한 ID입니다."}



# 사용자가 닉네임 입력 후 확인 버튼 클릭 시 동작
# 닉네임 규칙, 금칙어, 중복 체크
# 통과 시 True를 반환 
@router.post("/check/nickname")
async def router_nickname_check(nickname: str, db:AsyncSession = Depends(get_db))->Union[bool, dict]:
    # 규칙 체크
    if not utils_nickname_rule(nickname):
        raise HTTPException(status_code=400, detail="사용 불가한 닉네임 입니다.")
    
    # 금칙어 체크
    if not await repo_nickname_banned_keywords(db, nickname):
        raise HTTPException(status_code=400, detail="사용 불가한 단어입니다.")
    
    # 중복 체크
    if not await repo_nickname_exists(db, nickname):
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임 입니다.")

    return {"is_available": True, "message": "사용 가능한 닉네임입니다."}




# 사용자가 비밀번호 입력 후 확인 버튼 클릭 시 동작
# 비밀번호 규칙 체크
# 통과 시 True를 반환
@router.post("/check/password")
async def router_password_check(password: str, db:AsyncSession = Depends(get_db))->Union[bool, dict]:
    # 규칙 체크
    if not utils_password_rule(password):
        raise HTTPException(status_code=400, detail="사용 불가한 비밀번호 입니다.")
    return {"is_available": True, "message": "사용 가능한 비밀번호입니다."}