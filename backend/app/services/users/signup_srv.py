from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union 
from datetime import datetime
import logging

# 커스텀 모듈
from app.core.security import hash_password
from app.schemas.user_sch import sch_user_signup

from app.repositories.users.register_repo import repo_register_user
from app.repositories.check.duplicate_check_repo import repo_email_exists, repo_id_exists, repo_nickname_exists


logger = logging.getLogger(__name__)

async def srv_user_signup(request: Request, user: sch_user_signup, db:AsyncSession)->Union[bool, dict]:
    logger.info(f"Signup attempt for username={user.username}, email={user.email}, nickname={user.nickname}")

    # 2차 이메일 중복 체크
    if not await repo_email_exists(db, user.email):
        logger.warning(f"Signup failed: email already exists - {user.email}")
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")
    
    # 2차 아이디 중복 체크
    if not await repo_id_exists(db, user.username):
        logger.warning(f"Signup failed: username already exists - {user.username}")
        raise HTTPException(status_code=400, detail="이미 사용 중인 ID 입니다.")
        
    # 2차 닉네임 중복 체크
    if not await repo_nickname_exists(db, user.nickname):
        logger.warning(f"Signup failed: nickname already exists - {user.nickname}")
        raise HTTPException(status_code=400, detail="이미 사용 중인 닉네임입니다.")

    # 비밀번호 해시화
    password_hash = hash_password(user.password)
    logging.debug(f"Password hashed for username={user.username}")

    new_user = {
        "username":user.username,
        "nickname":user.nickname, 
        "password_hash":password_hash,
        "email":user.email,
        "notification":user.notification, 
        "advertising_consent": user.advertising_consent, 
        "terms_agreed": True,         
        "role": "user",              
        "status": "active"           
    }
    success = await repo_register_user(new_user, db)
    if not success:
        logger.error(f"Signup failed: unable to save user - {user.username}")
        raise HTTPException(status_code=500, detail="저장할 수 없습니다.")
    
    logger.info(f"Singup success for username={user.username}")
    # 없어도 되는 코드
    return True