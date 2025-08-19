from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Union
import logging

from app.F2_services.static_page import StaticPageService
from app.F5_core.dependencies import get_static_page_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.static_page import (
    StaticPageResponse, 
    StaticPagePathParams
)
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

router = APIRouter()

# 정적 페이지 조회 엔드포인트
@router.get("/{slug}", response_model=Union[StaticPageResponse, ErrorResponse])
@log_event_detailed(action="READ", category=["PUBLIC", "STATIC_PAGE"])
async def get_static_page(
    path_params: StaticPagePathParams = Depends(),
    static_page_service: StaticPageService = Depends(get_static_page_service)
):
    """
    정적 페이지 내용 조회
    
    - **목적**: 정적 페이지의 전체 내용 조회 (HTML 형태로 변환된 콘텐츠)
    - **사용 위치**: 푸터의 about, terms, privacy, youth-protection 상세 페이지
    - **인증**: 불필요
    - **권한**: 없음 (모든 사용자 접근 가능)
    - **응답**: 정적 페이지 내용 (Markdown에서 HTML로 변환됨)
    - **지원 slug**: about, terms, privacy, youth-protection
    """
    try:
        # 1. 정적 페이지 내용 조회 (Markdown → HTML 변환 포함)
        result = await static_page_service.get_static_page_by_slug(path_params.slug)
        
        # 2. 에러 응답인지 확인
        if isinstance(result, ErrorResponse):
            # Service에서 ErrorResponse 반환 시 500 상태 코드로 처리
            return JSONResponse(
                status_code=500,
                content=result.model_dump()
            )
        
        # 3. 성공 응답 반환
        return result
        
    except Exception as e:
        # 4. 예외 발생 시 로그 기록 및 에러 응답 반환
        logger.error(f"Failed to get static page for slug '{path_params.slug}': {e}", exc_info=True)
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message=Message.INTERNAL_ERROR
            )
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )