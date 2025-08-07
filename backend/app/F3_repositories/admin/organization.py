import logging

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload
from typing import List, Optional

from app.F7_models.organizations import Organization
from app.F7_models.categories import Category
from app.F7_models.feeds import Feed

logger = logging.getLogger(__name__)

class OrganizationAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # 기존 계획에 없던 건데 새롭게 추가한 것
    async def get_simple_organization_list(self) -> List[Organization]:
        """
        모든 활성화된 기관의 ID와 이름 목록을 조회
        """
        try:
            stmt = (
                select(Organization.id, Organization.name)
                .where(Organization.is_active == True)
                .order_by(Organization.name.asc())
            )
            result = await self.db.execute(stmt)
            # .mappings()를 사용하면 ORM 객체가 아닌 Dict-like 객체로 결과를 받습니다.
            return result.mappings().all()
        except Exception as e:
            logger.error(f"Error getting simple organization list: {e}", exc_info=True)
            return []
        
    async def get_organizations_with_categories(self) -> List[Organization]:
        """
        관리자: 모든 기관과 각 기관에 속한 카테고리, 그리고 각각의 피드 수를 조회
        N+1 문제를 방지하기 위해 selectinload를 사용
        """
        try:
            # 1. 기관별 피드 수를 계산하는 서브쿼리
            org_feed_counts = (
                select(Feed.organization_id, func.count(Feed.id).label("feed_count"))
                .group_by(Feed.organization_id)
                .subquery()
            )

            # 2. 카테고리별 피드 수를 계산하는 서브쿼리
            cat_feed_counts = (
                select(Feed.category_id, func.count(Feed.id).label("feed_count"))
                .group_by(Feed.category_id)
                .subquery()
            )

            # 3. 메인 쿼리
            stmt = (
                select(
                    Organization,
                    org_feed_counts.c.feed_count.label("organization_feed_count")
                )
                .outerjoin(org_feed_counts, Organization.id == org_feed_counts.c.organization_id)
                # categories 관계를 Eager Loading 하고, 그 안의 feed_count도 함께 로드
                .options(
                    selectinload(Organization.categories)
                )
                .order_by(Organization.name.asc())
            )
            
            result = await self.db.execute(stmt)
            organizations = result.scalars().unique().all()
            
            # SQLAlchemy 2.0에서는 위 쿼리만으로 관계가 로드
            # 카테고리별 피드 카운트는 서비스단에서 계산하거나, 별도 쿼리로 가져오는 것이 더 간단할 수 있음
            # 우선은 기관별 피드 카운트만 적용하고, 카테고리 카운트는 서비스에서 처리
            
            # 위 쿼리로는 카테고리별 피드 카운트를 직접 가져오기 복잡하므로,
            # 별도 쿼리로 모든 카테고리의 피드 카운트를 가져옴
            cat_counts_query = select(Category.id, func.count(Feed.id).label("feed_count")).join(Feed).group_by(Category.id)
            cat_counts_result = await self.db.execute(cat_counts_query)
            cat_counts_map = {row[0]: row[1] for row in cat_counts_result.all()}

            # 로드된 객체에 피드 카운트 정보를 추가
            for org in organizations:
                org.feed_count = next((row.organization_feed_count for row in result.all() if row.Organization.id == org.id), 0) or 0
                for cat in org.categories:
                    cat.feed_count = cat_counts_map.get(cat.id, 0)
            
            return list(organizations)
        except Exception as e:
            logger.error(f"Error getting organizations with categories: {e}", exc_info=True)
            return []
        
