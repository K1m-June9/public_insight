import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.F6_schemas.base import ErrorResponse, ErrorCode
from app.F6_schemas.search import (
    SearchQuery,
    SearchResponse,
)

from app.F5_core.logging_decorator import log_event_detailed
from app.F11_search.ES8_search_service import search_contents

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "",
    response_model=SearchResponse,
    # [수정] API 문서에 실제 가능한 오류만 명시
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 파라미터"},
        500: {"model": ErrorResponse, "description": "검색 엔진 오류"}
    }
)
@log_event_detailed(action="SEARCH", category=["PUBLIC", "GLOBAL_SEARCH"])
async def get_search_results(
    query_params: SearchQuery = Depends(),
    request: Request = None
):
    """
    Elasticsearch를 통해 콘텐츠를 검색하고 결과를 반환합니다.
    - **성공 시:** HTTP 200 OK와 함께 `SearchResponse` 반환
    - **실패 시:**
        - 잘못된 파라미터 (400): `ErrorCode.INVALID_PARAMETER`
        - 검색 엔진 오류 (500): `ErrorCode.SEARCH_ENGINE_ERROR`
    """
    # [수정] 서비스가 항상 응답 객체를 반환하므로 라우터의 최상위 try-except는 제거 가능 (유지해도 무방)
    if request:
        logger.info(f"Received search request from {request.client.host}: {request.url.query}")
    else:
        logger.info(f"Received search request with params: {query_params.dict()}")

    result = await search_contents(query_params=query_params)
    
    # 서비스가 ErrorResponse를 반환하면, 이는 항상 500 에러임
    if isinstance(result, ErrorResponse):
        status_code = 500
        if result.error.code == ErrorCode.INVALID_PARAMETER:
            status_code = 400
        elif result.error.code == ErrorCode.SEARCH_TIMEOUT:
            status_code = 503

        return JSONResponse(
            status_code=status_code,
            content=result.model_dump()
        )
    
    return result