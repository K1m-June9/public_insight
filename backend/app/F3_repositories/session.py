from typing import List, Optional
from sqlalchemy import select, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.F7_models.refresh_token import RefreshToken

class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: int) -> List[RefreshToken]:
        """user_id로 모든 리프레시 토큰(세션) 조회"""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        return result.scalars().all()

    async def get_sessions(
        self,
        user_id: Optional[int] = None,
        active_only: bool = True
    ) -> List[RefreshToken]:
        """
        user_id가 주어지면 해당 사용자의 세션을 조회하며,
        active_only=True면 만료되지 않고 무효화되지 않은(유효한) 세션만 반환합니다
        """
        query = select(RefreshToken)
        if user_id is not None:
            query = query.where(RefreshToken.user_id == user_id)
        if active_only:
            query = query.where(
                and_(
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        result = await self.db.execute(query)
        return result.scalars().all()

    # id 아니어도 됨
    async def get_by_id(self, id: int) -> Optional[RefreshToken]:
        """session_id로 단일 세션 조회"""
        return await self.db.get(RefreshToken, id)

    # /reset-password 사용
    async def revoke_all_for_user(self, user_id: str):
        """특정 user_id에 속한 모든 리프레시 토큰을 무효화(revoked=True)"""
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.db.commit()
