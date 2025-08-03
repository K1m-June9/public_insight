import logging
from typing import Union

from app.F3_repositories.admin.static_page import StaticPageAdminRepository
from app.F6_schemas.admin.static_page import StaticPageListResponse, StaticPageListItem
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

class StaticPageAdminService:
    """
    관리자 기능 - 정적 페이지 관련 비즈니스 로직을 처리하는 클래스
    """
    def __init__(self, repo: StaticPageAdminRepository):
        self.repo = repo

    async def get_static_pages_list(self) -> Union[StaticPageListResponse, ErrorResponse]:
        """
        모든 정적 페이지의 목록을 조회하고, API 응답 스키마에 맞게 변환

        Returns:
            Union[StaticPageListResponse, ErrorResponse]: 성공 시 페이지 목록, 실패 시 에러 응답
        """
        try:
            # 1. Repository를 통해 모든 StaticPage ORM 객체를 가져옴
            pages = await self.repo.get_all_static_pages()

            # 2. ORM 객체를 응답 스키마(StaticPageListItem)로 변환
            page_items = []
            for page in pages:
                # Settings에 정의된 FIXED_PAGES에서 slug에 맞는 title을 가져옴
                title = Settings.FIXED_PAGES.get(page.slug, "알 수 없는 페이지")
                
                item = StaticPageListItem(
                    id=page.id,
                    slug=page.slug,
                    title=title,
                    #content=page.content,
                    created_at=page.created_at,
                    updated_at=page.updated_at
                )
                page_items.append(item)
            
            # 3. 최종 응답 객체를 생성하여 반환
            return StaticPageListResponse(
                    success=True,
                    data=page_items
                    )

        except Exception as e:
            logger.error(f"Error in get_static_pages_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )