from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Union
import logging

from app.F2_services.notice import NoticeService
from app.F5_core.dependencies import get_notice_service
from app.F6_schemas.base import (
    PaginationQuery, ErrorResponse, ErrorDetail, ErrorCode, Message
)
from app.F6_schemas.notice import (
    PinnedNoticeResponse, NoticeListQuery, NoticeListResponse,
    NoticeDetailResponse, PinnedNoticeData
)


router = APIRouter()


logger = logging.getLogger(__name__)

# 공지사항 목록 조회
# 공지사항 페이지에서 전체 공지사항 목록 조회
@router.get("", response_model=NoticeListResponse)
async def read_notices(
    query: PaginationQuery = Depends(),
    notice_service: NoticeService = Depends(get_notice_service)
):
    """
    공지사항 페이지 : 전체 공지사항 목록 조회
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    
    """
    notice_query =  NoticeListQuery(
        page= query.page,
        limit = query.limit
    )
    
    result = await notice_service.get_main_notice_list(notice_query)
    
    if isinstance(result, ErrorResponse):
        # INTERNAL_SERVER_ERROR의 경우 500 상태 코드로 응답
        status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())   
    
    return result


# 중요(고정된) 게시물
@router.get("/pinned", response_model=PinnedNoticeResponse)
async def pinned_notices(
    notice_service: NoticeService = Depends(get_notice_service)
):
    """메인 페이지에 표시할 고정된 공지사항 조회"""
    # 1. 고정된 공지사항 데이터를 조회
    result = await notice_service.get_pinned_notice()
    
    # 2. 결과가 ErrorResponse 타입이라면 에러 응답 처리
    if isinstance(result, ErrorResponse):
        # 에러 코드에 관계없이 기본적으로 HTTP 500 상태로 처리
        status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())  
    
    # 3. 성공적으로 조회된 경우 PinnedNoticeResponse 객체 반환
    return result



@router.get("/{id}", response_model=Union[NoticeDetailResponse, ErrorResponse])
async def get_notice_detail(
    id: int,
    notice_service: NoticeService = Depends(get_notice_service)
):  
    try:
        # 1. 공지사항 상세 정보 조회
        result = await notice_service.get_notice_detail(id)
        
        # 2. 에러 응답인지 확인
        if isinstance(result, ErrorResponse):
            # 에러 코드에 따라 HTTP 상태코드 설정
            if result.error.code == "NOTICE_NOT_FOUND":
                status_code = 404
            elif result.error.code == "INVALID_NOTICE_ID":
                status_code = 400
            else:
                status_code = 500
            
            return JSONResponse(
                status_code=status_code,
                content=result.model_dump()
            )
        
        # 3. 성공 응답 반환
        return result
        
    except Exception as e:
        # 4. 예외 발생 시 로그 기록 및 에러 응답 반환
        logger.error(f"공지사항 상세 응답 중 서버 오류 발생 - id: {id}, error: {e}", exc_info=True)
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