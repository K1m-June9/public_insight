from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import uuid
import random
import logging
from fastapi import HTTPException, status, Depends, BackgroundTasks

from app.F3_repositories.users import UserRepository
from app.F4_utils.validators import validate_nickname, validate_password
from app.F5_core.security import auth_handler

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository):
        # UserRepository 인스턴스를 주입받아 DB 접근에 사용
        self.repo = repo

    async def update_nickname(self, user_id: str, nickname: str) -> Optional[str]:
        """nickname 변경"""
        
        # 1. 유효성 검사
        if not validate_nickname(nickname):
            logger.info(f"Nickname validation failed: {nickname}")
            return None 

        # 2. 중복 검사 (본인 제외)
        exists = await self.repo.is_nickname_exists(nickname, exclude_user_id=user_id)
        if exists:
            logger.info(f"Nickname exists check: {nickname} => {exists}")
            return None
        
        # 3. 닉네임 업데이트
        await self.repo.update_nickname(user_id, nickname)
        return nickname
    

    async def update_password(self, user_id: str, current_password: str, new_password: str):
        """비밀번호 변경"""
        user = await self.repo.get_user_by_user_id(user_id)
        
        # 1. 현재 비밀번호 검사
        if not auth_handler.verify_password(current_password, user.password_hash):
            logger.warning(f"[{user_id}] 현재 비밀번호가 일치하지 않음")
            return False
        

        # 2. current_password와 new_password가 동일하면 안됨
        if auth_handler.verify_password(new_password, user.password_hash):
            logger.warning(f"[{user_id}] 새 비밀번호가 기존 비밀번호와 동일함")
            return False


        # 3. 새로운 비밀번호 유효성 검사
        if not validate_password(new_password):
            logger.info(f"[{user_id}] 새 비밀번호 유효성 검사 실패")
            return False
        

        # 4. 비밀번호 해시 및 업데이트
        new_hash = auth_handler.get_password_hash(new_password)
        await self.repo.update_password(user_id, new_hash)
        
        logger.info(f"[{user_id}] 비밀번호 변경 완료")
        return True