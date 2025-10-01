import logging
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, raiseload, noload

from app.F7_models.feeds import Feed

logger = logging.getLogger(__name__)

class RecommendationRepository:
    """
    추천 시스템에 필요한 데이터를 데이터베이스에서 조회하는 리포지토리.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_feeds_for_fitting(self) -> List[Feed]:
        """
        추천 엔진 학습에 필요한 모든 피드의 최소 정보를 조회함.
        성능을 위해 category 정보만 Eager Loading하고 나머지는 로드하지 않음.
        """
        try:
            stmt = (
                # 💥 Feed 객체 전체를 선택하도록 수정
                select(Feed)
                .options(
                    # category 관계는 반드시 필요하므로 Eager Loading
                    selectinload(Feed.category),
                    # 다른 불필요한 관계(organization, bookmarks 등)는 로드하지 않도록 하여 성능 최적화
                    noload(Feed.organization),
                    noload(Feed.bookmarks),
                    noload(Feed.ratings)
                )
                .where(Feed.is_active == True)
            )
            result = await self.db.execute(stmt)
            # 💥 이제 scalars()와 unique()를 사용하여 Feed 객체 리스트를 올바르게 가져올 수 있음
            feeds = result.scalars().unique().all()
            return feeds
        
        except Exception as e:
            logger.error(f"Error getting all feeds for fitting: {e}", exc_info=True)
            return []

    async def get_feeds_by_ids(self, feed_ids: List[int]) -> List[Feed]:
        """
        주어진 ID 목록에 해당하는 피드들의 상세 정보를 조회합니다.
        """
        if not feed_ids:
            return []
        try:
            stmt = (
                select(Feed)
                .where(Feed.id.in_(feed_ids))
                .options(
                    selectinload(Feed.organization), # 응답에 필요한 정보들을 Eager Loading
                    selectinload(Feed.category)
                )
            )
            result = await self.db.execute(stmt)
            feeds = result.scalars().unique().all()
            
            # 원본 ID 목록의 순서를 유지하기 위해 결과를 다시 정렬
            feed_map = {feed.id: feed for feed in feeds}
            sorted_feeds = [feed_map[id] for id in feed_ids if id in feed_map]

            return sorted_feeds

        except Exception as e:
            logger.error(f"Error getting feeds by IDs: {e}", exc_info=True)
            return []