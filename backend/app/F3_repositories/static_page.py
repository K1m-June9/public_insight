from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import logging
from app.F7_models.static_pages import StaticPage

logger = logging.getLogger(__name__)

class StaticPageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # slug를 기준으로 정적 페이지 조회 메서드
    # 입력: 
    #   slug - 조회할 정적 페이지의 식별자 (str)
    # 반환: 
    #   조회된 StaticPage 객체 또는 None (존재하지 않는 경우)
    # 설명: 
    #   주어진 slug에 해당하는 정적 페이지를 조회하여 반환
    #   존재하지 않는 slug인 경우 None을 반환하여 Service 레이어에서 처리하도록 함
    #   content는 원본 Markdown 형태 그대로 반환 (HTML 변환은 Service에서 처리)
    async def get_by_slug(self, slug: str) -> Optional[StaticPage]:
        query = select(StaticPage).where(StaticPage.slug == slug)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()