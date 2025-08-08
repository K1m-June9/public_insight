from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.F7_models.organizations import Organization

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