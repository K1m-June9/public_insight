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
        관리자: 모든 기관과 각 기관에 속한 카테고리 목록 및 피드 수를 효율적으로 조회
        """
        try:
            # 1. [DB 쿼리 1] 모든 기관과 그에 속한 카테고리들을 Eager Loading으로 한 번에 가져옴
            #    'selectinload'는 N+1 문제를 방지하는 가장 효율적인 방법 중 하나
            org_stmt = (
                select(Organization)
                .options(selectinload(Organization.categories))
                .order_by(Organization.name.asc())
            )
            org_result = await self.db.execute(org_stmt)
            organizations = org_result.scalars().unique().all()

            if not organizations:
                return []

            # 2. 파이썬에서 필요한 ID 목록들을 미리 추출
            org_ids = [org.id for org in organizations]
            all_category_ids = [cat.id for org in organizations for cat in org.categories]
            
            # 3. [DB 쿼리 2] 기관별 피드 수를 한 번의 쿼리로 모두 가져옴
            org_counts_stmt = (
                select(Feed.organization_id, func.count(Feed.id))
                .where(Feed.organization_id.in_(org_ids))
                .group_by(Feed.organization_id)
            )
            org_counts_result = await self.db.execute(org_counts_stmt)
            # 결과를 {기관ID: 피드수} 형태의 딕셔너리(맵)으로 변환하여 조회 성능을 높임
            org_counts_map = {org_id: count for org_id, count in org_counts_result}

            # 4. [DB 쿼리 3] 카테고리별 피드 수를 한 번의 쿼리로 모두 가져옴
            cat_counts_stmt = (
                select(Feed.category_id, func.count(Feed.id))
                .where(Feed.category_id.in_(all_category_ids))
                .group_by(Feed.category_id)
            )
            cat_counts_result = await self.db.execute(cat_counts_stmt)
            # 결과를 {카테고리ID: 피드수} 형태의 딕셔너리로 변환
            cat_counts_map = {cat_id: count for cat_id, count in cat_counts_result}
            
            # 5. 파이썬 루프를 통해 메모리에서 데이터 최종 조합
            #    이 과정은 DB와 통신하지 않으므로 매우 빠름
            for org in organizations:
                org.feed_count = org_counts_map.get(org.id, 0)
                for cat in org.categories:
                    cat.feed_count = cat_counts_map.get(cat.id, 0)

            return organizations
            
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
            # await self.db.commit()
            await self.db.flush()

            result = await self.db.execute(
                select(Organization)
                .options(selectinload(Organization.categories))
                .where(Organization.id == new_organization.id)
            )

            org_with_cateogires = result.scalar_one()
            return org_with_cateogires
            
            
        except Exception as e:
            logger.error(f"Error creating organization '{name}': {e}", exc_info=True)
            raise # 서비스 레이어에서 처리하도록 예외를 다시 발생시킴

    async def create_category(self, name: str, description: Optional[str], organization_id: int, is_active: bool) -> Category:
        """
        새로운 카테고리를 생성
        """
        try:
            # 1. Organization 객체 가져오기
            org = await self.db.get(Organization, organization_id)
            if not org: 
                raise ValueError(f"Organization {organization_id} not found")
            

            # 2. Category 객체 생성 시 관계 연결
            new_category = Category(
                name=name,
                description=description,
                organization=org,
                is_active=is_active
            )
            self.db.add(new_category)

            # 3. flush 해서 PK 확보
            await self.db.flush()
            
            # 4. 관계를 안전하게 로드
            await self.db.refresh(
                new_category,
                attribute_names=["organization", "created_at", "updated_at"]
            )

            # 5. 반환
            return new_category
        except Exception as e:
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
            
            return result.rowcount > 0
        except Exception as e:
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
            return result.rowcount > 0
        
        except Exception as e:
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
            return True
        
        except Exception as e:
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
            return True
        
        except Exception as e:
            logger.error(f"Error deleting category {cat_id}: {e}", exc_info=True)
            return False
        
    async def get_organization_by_name(self, name: str) -> Optional[Organization]:
        result = await self.db.execute(select(Organization).where(Organization.name == name))
        return result.scalar_one_or_none()

    async def is_category_name_duplicate(self, org_id: int, name: str) -> bool:
        result = await self.db.execute(
            select(func.count(Category.id)).where(
                Category.organization_id == org_id,
                Category.name == name
            )
        )
        return result.scalar_one() > 0