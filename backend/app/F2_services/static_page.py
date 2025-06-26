from typing import Optional
import logging
import markdown
from app.F3_repositories.static_page import StaticPageRepository
from app.F6_schemas.static_page import StaticPageResponse, StaticPageContent, StaticPageData
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class StaticPageService:
    def __init__(self, repository: StaticPageRepository):
        self.repository = repository
        # Markdown 변환기 초기화 (테이블, 코드 하이라이팅 등 확장 기능 포함)
        self.markdown_converter = markdown.Markdown(
            extensions=[
                'tables',           # 테이블 지원
                'codehilite',       # 코드 하이라이팅
                'fenced_code',      # 펜스 코드 블록
                'toc',              # 목차 생성
                'nl2br',            # 줄바꿈 처리
                'sane_lists'        # 리스트 처리 개선
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
    
    # slug를 기준으로 정적 페이지 조회 및 HTML 변환 메서드
    # 입력: 
    #   slug - 조회할 정적 페이지의 식별자 (str)
    # 반환: 
    #   StaticPageResponse - 성공 시 HTML로 변환된 페이지 내용
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   1. Repository를 통해 주어진 slug의 정적 페이지를 조회
    #   2. 페이지가 존재하지 않으면 "invalid-page" slug로 재조회
    #   3. "invalid-page"도 존재하지 않으면 500 에러 반환
    #   4. 조회 성공 시 Markdown content를 HTML로 변환하여 반환
    #   5. 관리자가 작성한 content이므로 별도 보안 처리 없이 변환
    async def get_static_page_by_slug(self, slug: str) -> StaticPageResponse:
        try:
            # 1단계: 요청된 slug로 페이지 조회
            static_page = await self.repository.get_by_slug(slug)
            
            # 2단계: 페이지가 없으면 invalid-page로 재조회
            if static_page is None:
                logger.warning(f"Static page not found for slug: {slug}, trying invalid-page")
                static_page = await self.repository.get_by_slug("invalid-page")
                
                # 3단계: invalid-page도 없으면 500 에러 반환
                if static_page is None:
                    logger.error("Invalid-page not found in database")
                    return ErrorResponse(
                        error=ErrorDetail(
                            code=ErrorCode.INTERNAL_ERROR,
                            message=Message.INTERNAL_ERROR
                        )
                    )
            
            # 4단계: Markdown content를 HTML로 변환
            html_content = self.markdown_converter.convert(static_page.content)
            
            # 5단계: 응답 스키마로 변환하여 반환
            return StaticPageResponse(
                data=StaticPageData(
                    page=StaticPageContent(
                        slug=static_page.slug,
                        content=html_content
                    )
                )
            )
            
        except Exception as e:
            # 예상치 못한 에러 발생 시 로깅 및 500 에러 반환
            logger.error(f"Unexpected error in get_static_page_by_slug: {str(e)}")
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )