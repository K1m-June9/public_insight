from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.F7_models.static_pages import StaticPage
from app.F7_models.static_page_versions import StaticPageVersion

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
        
    async def get_page_by_slug(self, slug: str) -> Optional[StaticPage]:
        """
        slug를 기준으로 특정 정적 페이지를 조회

        Args:
            slug (str): 조회할 페이지의 slug

        Returns:
            Optional[StaticPage]: StaticPage ORM 객체 또는 None
        """
        result = await self.db.execute(
            select(StaticPage).where(StaticPage.slug == slug)
        )
        return result.scalar_one_or_none()

    async def update_page_content(self, slug: str, new_content: str) -> Optional[StaticPage]:
        """
        특정 정적 페이지의 content를 업데이트하고, 변경 이력을 기록

        Args:
            slug (str): 업데이트할 페이지의 slug
            new_content (str): 새로운 content 내용

        Returns:
            Optional[StaticPage]: 업데이트된 StaticPage ORM 객체 또는 None
        """
        # 1. 먼저 업데이트할 페이지 객체를 조회
        page = await self.get_page_by_slug(slug)
        if not page:
            return None #없으면 안되긴 해
            
        # 2. 변경 이력을 StaticPageVersion 테이블에 저장
        version = StaticPageVersion( #캬 이거 드디어 써보네
            page_id=page.id,
            content=new_content  # 변경된 내용을 저장
        )
        self.db.add(version)

        # 3. 기존 페이지의 content를 업데이트
        page.content = new_content
        # 'updated_at'은 onupdate 설정으로 자동 갱신 ㅖㅖ

        await self.db.commit()
        await self.db.refresh(page)
        
        return page