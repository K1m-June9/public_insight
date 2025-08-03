import logging
from typing import Union

from app.F3_repositories.admin.static_page import StaticPageAdminRepository
from app.F6_schemas.admin.static_page import (
    StaticPageListResponse, 
    StaticPageListItem,
    StaticPageDetail,
    StaticPageDetailResponse,
    StaticPageUpdateResponse
    )
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
        
    async def get_static_page_detail(self, slug: str) -> Union[StaticPageDetailResponse, ErrorResponse]:
        """
        특정 slug를 가진 정적 페이지의 상세 정보를 조회

        Args:
            slug (str): 조회할 페이지의 slug

        Returns:
            Union[StaticPageDetailResponse, ErrorResponse]: 성공 시 상세 정보, 실패 시 에러 응답
        """
        try:
            page = await self.repo.get_page_by_slug(slug)

            if not page:
                return ErrorResponse(error=ErrorDetail(
                    code=ErrorCode.NOT_FOUND,
                    message=Message.PAGE_NOT_FOUND
                    )
                )
            
            title = Settings.FIXED_PAGES.get(page.slug, "알 수 없는 페이지")
            
            page_detail = StaticPageDetail(
                id=page.id,
                slug=page.slug,
                title=title,
                content=page.content,
                created_at=page.created_at,
                updated_at=page.updated_at
            )
            
            return StaticPageDetailResponse(
                success=True,
                data=page_detail
            )
            
        except Exception as e:
            logger.error(f"Error in get_static_page_detail for slug {slug}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def update_static_page(self, slug: str, content: str) -> Union[StaticPageUpdateResponse, ErrorResponse]:
        """
        특정 정적 페이지의 내용을 수정

        Args:
            slug (str): 수정할 페이지의 slug
            content (str): 새로운 content 내용

        Returns:
            Union[StaticPageUpdateResponse, ErrorResponse]: 성공 시 수정된 정보, 실패 시 에러 응답
        """
        try:
            # 1. 입력값 유효성 검증
            if not content or not content.strip():
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.BAD_REQUEST,
                        message=Message.EMPTY_CONTENT_ERROR
                        )
                    )

            # 2. Repository를 통해 페이지 업데이트
            updated_page = await self.repo.update_page_content(slug, content)

            if not updated_page:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.PAGE_NOT_FOUND
                        )
                    )

            # 3. 성공 응답 생성
            title = Settings.FIXED_PAGES.get(updated_page.slug, "알 수 없는 페이지")

            page_detail = StaticPageDetail(
                id=updated_page.id,
                slug=updated_page.slug,
                title=title,
                content=updated_page.content,
                created_at=updated_page.created_at,
                updated_at=updated_page.updated_at
            )
            
            return StaticPageUpdateResponse(
                success=True,
                data=page_detail
                )

        except Exception as e:
            logger.error(f"Error in update_static_page for slug {slug}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                    )
                )