# 파일 위치: backend/app/F2_services/admin/organization.py

import logging
from typing import Union, List

from app.F3_repositories.admin.organization import OrganizationAdminRepository
from app.F6_schemas.admin.organization import (
    SimpleOrganizationListResponse, 
    SimpleOrganizationItem,
    OrganizationListResponse, 
    OrganizationWithCategories, 
    CategoryItem
)
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class OrganizationAdminService:
    def __init__(self, repo: OrganizationAdminRepository):
        self.repo = repo

    async def get_simple_list(self) -> Union[SimpleOrganizationListResponse, ErrorResponse]:
        try:
            organizations = await self.repo.get_simple_organization_list()
            org_items = [SimpleOrganizationItem(id=org['id'], name=org['name']) for org in organizations]
            return SimpleOrganizationListResponse(data=org_items)
        except Exception as e:
            logger.error(f"Error in get_simple_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def get_organizations_list(self) -> Union[OrganizationListResponse, ErrorResponse]:
        """
        관리자: 모든 기관과 각 기관에 속한 카테고리 목록을 조회합니다.
        """
        try:
            # 1. Repository를 통해 모든 필요한 데이터가 포함된 ORM 객체 리스트를 가져옴
            organizations = await self.repo.get_organizations_with_categories()

            # 2. ORM 객체를 API 응답 스키마 형태로 변환
            response_data: List[OrganizationWithCategories] = []
            for org in organizations:
                # 2-1. 각 기관에 속한 카테고리들을 CategoryItem 스키마로 변환
                category_items = [
                    CategoryItem(
                        id=cat.id,
                        name=cat.name,
                        description=cat.description,
                        is_active=cat.is_active,
                        feed_count=getattr(cat, 'feed_count', 0), # getattr로 안전하게 접근
                        created_at=cat.created_at,
                        updated_at=cat.updated_at
                    ) for cat in sorted(org.categories, key=lambda c: c.name) # 카테고리 이름순 정렬
                ]

                # 2-2. 최종 OrganizationWithCategories 스키마로 조합
                org_item = OrganizationWithCategories(
                    id=org.id,
                    name=org.name,
                    description=org.description,
                    website_url=org.website_url,
                    is_active=org.is_active,
                    feed_count=getattr(org, 'feed_count', 0),
                    created_at=org.created_at,
                    updated_at=org.updated_at,
                    categories=category_items
                )
                response_data.append(org_item)
            
            # 3. 최종 응답 객체를 생성하여 반환합니다.
            return OrganizationListResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error in get_organizations_list: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))