from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.F7_models.static_pages import StaticPage

logger = logging.getLogger(__name__)

class StaticPageAdminRepository:
    """
    관리자 기능 - 정적 페이지 관련 데이터베이스 작업을 처리하는 클래스
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_static_pages(self) -> List[StaticPage]:
        """
        모든 정적 페이지 목록 조회

        Returns:
            List[StaticPage]: StaticPage ORM 객체들의 리스트
        """
        try:
            stmt = select(StaticPage).order_by(StaticPage.id.asc())
            result = await self.db.execute(stmt)
            pages = result.scalars().all()
            return list(pages)
        except Exception as e:
            logger.error(f"Error getting all static pages: {e}", exc_info=True)
            # 서비스 레이어에서 처리할 수 있도록 예외를 다시 발생시키거나 빈 리스트를 반환
            # 여기서는 빈 리스트를 반환하여 서비스가 안정적으로 처리하도록 함
            return []