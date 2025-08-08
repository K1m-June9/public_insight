import logging

from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, subqueryload
from typing import List, Optional, Dict, Any

from app.F6_schemas.base import Settings

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
        
    async def create_organization(self, name: str, description: Optional[str], website_url: Optional[str]) -> Organization:
        """
        새로운 기관과 기본 '보도자료' 카테고리를 생성
        is_active의 기본값은 모델 정의(default=False)를 따름

        Args:
            name (str): 기관명
            description (Optional[str]): 기관 설명
            website_url (Optional[str]): 웹사이트 URL

        Returns:
            Organization: 생성된 Organization ORM 객체
        """
        try:
            # 1. 새로운 Organization 객체 생성
            new_organization = Organization(
                name=name,
                description=description,
                website_url=website_url
            )

            # 2. 기본 '보도자료' 카테고리 생성 및 연결
            # Settings.PROTECTED_CATEGORY_NAME = "보도자료"
            default_category = Category(
                name=Settings.PROTECTED_CATEGORY_NAME,
                organization=new_organization
            )
            
            self.db.add(new_organization)
            # 카테고리는 관계에 의해 자동으로 함께 추가
            
            await self.db.commit()
            await self.db.refresh(new_organization)
            
            # 관계 로드를 위해 Eager Loading 옵션과 함께 다시 조회할 수도 있지만,
            # 지금은 생성된 객체만 반환해도 충분
            return new_organization
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating organization '{name}': {e}", exc_info=True)
            raise # 서비스 레이어에서 처리하도록 예외를 다시 발생시킴

    async def create_category(self, name: str, description: Optional[str], organization_id: int, is_active: bool) -> Category:
        """
        새로운 카테고리를 생성
        """
        try:
            new_category = Category(
                name=name,
                description=description,
                organization_id=organization_id,
                is_active=is_active
            )
            self.db.add(new_category)
            await self.db.commit()
            await self.db.refresh(new_category, attribute_names=['organization']) # 'organization' 관계 로드
            return new_category
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating category '{name}' for org_id {organization_id}: {e}", exc_info=True)
            raise

    async def update_organization(self, org_id: int, update_data: Dict[str, Any]) -> bool:
        """
        특정 기관의 정보를 수정
        """
        try:
            stmt = (
                update(Organization)
                .where(Organization.id == org_id)
                .values(**update_data)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating organization {org_id}: {e}", exc_info=True)
            return False
        
    async def get_category_by_id(self, cat_id: int) -> Optional[Category]:
        """
        ID로 특정 카테고리를 조회 (기관 정보 포함)
        """
        stmt = select(Category).options(selectinload(Category.organization)).where(Category.id == cat_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def update_category(self, cat_id: int, update_data: Dict[str, Any]) -> bool:
        """
        특정 카테고리의 정보를 수정
        """
        try:
            stmt = update(Category).where(Category.id == cat_id).values(**update_data)
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating category {cat_id}: {e}", exc_info=True)
            return False
        
    async def get_organization_by_id(self, org_id: int) -> Optional[Organization]:
        """
        ID로 특정 기관의 ORM 객체를 조회
        """
        result = await self.db.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_feed_count_for_organization(self, org_id: int) -> int:
        """
        특정 기관에 속한 피드의 총 개수를 계산
        """
        result = await self.db.execute(
            select(func.count(Feed.id)).where(Feed.organization_id == org_id)
        )
        return result.scalar_one()

    async def get_feed_count_for_category(self, cat_id: int) -> int:
        """
        특정 카테고리에 속한 피드의 총 개수를 계산
        """
        result = await self.db.execute(
            select(func.count(Feed.id)).where(Feed.category_id == cat_id)
        )
        return result.scalar_one()
    
    async def delete_organization(self, org_id: int) -> bool:
        """
        특정 기관을 삭제
        Organization 모델의 cascade 설정에 따라 연관된 categories도 함께 삭제
        """
        try:
            # 먼저 삭제할 객체를 가져옵니다.
            org_to_delete = await self.db.get(Organization, org_id)
            if not org_to_delete:
                return False

            await self.db.delete(org_to_delete)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting organization {org_id}: {e}", exc_info=True)
            return False
        
    async def delete_category(self, cat_id: int) -> bool:
        """
        특정 카테고리를 삭제
        """
        try:
            category_to_delete = await self.db.get(Category, cat_id)
            if not category_to_delete:
                return False
            await self.db.delete(category_to_delete)
            await self.db.commit()
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting category {cat_id}: {e}", exc_info=True)
            return False