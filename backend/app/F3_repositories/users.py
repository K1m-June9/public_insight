from sqlalchemy import select, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import logging

from app.F7_models.users import User

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    

    async def is_nickname_exists(self, nickname: str, exclude_user_id: str | None = None) -> bool:
        """nickname 중복 여부 확인"""
        stmt = select(User).where(User.nickname == nickname)
        if exclude_user_id:
            stmt = stmt.where(User.user_id != exclude_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def update_nickname(self,user_id: str, new_nickname: str):
        """사용자의 닉네임 변경"""
        # user_id와 일치하는 사용자 조회
        result = await self.db.execute(
            select(User).where((User.user_id == user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")
        
        if user.nickname == new_nickname:
            return # 변경 없음
        
        user.nickname = new_nickname
        await self.db.commit()
        await self.db.refresh(user)
    

    # user_id(사용자 아이디)를 기준으로 User 객체를 DB에서 조회하는 함수
    # 입력: user_id
    # 반환: User 객체 또는 조회 실패 시 None
    async def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()
    

    async def update_password(self, user_id: str, password: str):
        """비밀번호 변경"""
        # 1. user_id로 사용자 조회
        result = await self.db.execute(
            select(User).where((User.user_id == user_id)))
        user = result.scalar_one_or_none()

        # 2. 사용자가 존재하지 않으면 예외 발생
        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")
        
        # 3. 비밀번호 해시 업데이트
        user.password_hash = password
        await self.db.commit()
        await self.db.refresh(user)
    