import logging
import math
from typing import Union

from app.F3_repositories.admin.feed import FeedAdminRepository
from app.F6_schemas.admin.feed import OrganizationCategoriesResponse, OrganizationCategory, FeedListResponse, FeedListItem, FeedStatus, FeedListData
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, PaginationInfo

logger = logging.getLogger(__name__)

class FeedAdminService:
    """
    관리자 기능 - 피드 관리 관련 비즈니스 로직을 처리하는 클래스
    """
    def __init__(self, repo: FeedAdminRepository):
        self.repo = repo

    async def get_organization_categories(self, organization_id: int) -> Union[OrganizationCategoriesResponse, ErrorResponse]:
        """
        특정 기관에 속한 모든 활성화된 카테고리 목록을 조회

        Args:
            organization_id (int): 조회할 기관의 ID

        Returns:
            Union[OrganizationCategoriesResponse, ErrorResponse]: 성공 시 카테고리 목록, 실패 시 에러 응답
        """
        try:
            # 1. Repository를 통해 Category ORM 객체 리스트를 가져옴
            categories = await self.repo.get_categories_by_organization(organization_id)
            
            # Repository에서 빈 리스트를 반환해도 에러가 아니므로, 그대로 처리
            
            # 2. ORM 객체를 응답 스키마(OrganizationCategory)로 변환
            category_items = [
                OrganizationCategory(
                    id=cat.id,
                    name=cat.name,
                    is_active=cat.is_active
                ) for cat in categories
            ]
            
            # 3. 최종 응답 객체를 생성하여 반환
            return OrganizationCategoriesResponse(
                success=True,
                data=category_items
                )

        except Exception as e:
            logger.error(f"Error in get_organization_categories for org_id {organization_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def get_feeds_list(
            self,
            page: int,
            limit: int,
            search: str | None,
            organization_id: int | None,
            category_id: int | None
        ) -> Union[FeedListResponse, ErrorResponse]:
            """
            관리자 페이지: 피드 목록을 페이지네이션, 검색, 필터링하여 조회
            """
            try:
                # 1. Repository를 통해 피드 목록과 전체 개수를 가져옴
                feeds, total_count = await self.repo.get_feeds_list(
                    page=page,
                    limit=limit,
                    search=search,
                    organization_id=organization_id,
                    category_id=category_id
                )

                # 2. 페이지네이션 정보를 계산
                total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
                
                pagination_info = PaginationInfo(
                    current_page=page,
                    total_pages=total_pages,
                    total_count=total_count,
                    limit=limit,
                    has_next=page < total_pages,
                    has_previous=page > 1
                )

                # 3. Repository 데이터를 응답 스키마(FeedListItem)로 변환
                feed_items = [
                    FeedListItem(
                        id=feed["id"],
                        title=feed["title"],
                        organization_name=feed["organization_name"],
                        category_name=feed["category_name"],
                        status=FeedStatus.ACTIVE if feed["is_active"] else FeedStatus.INACTIVE,
                        view_count=feed["view_count"],
                        created_at=feed["created_at"]
                    ) for feed in feeds
                ]

                response_data = FeedListData(feeds=feed_items, pagination=pagination_info)
                return FeedListResponse(
                    success=True,
                    data=response_data
                    )

            except Exception as e:
                logger.error(f"Error in get_feeds_list: {e}", exc_info=True)
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INTERNAL_ERROR, 
                        message=Message.INTERNAL_ERROR
                        )
                    )