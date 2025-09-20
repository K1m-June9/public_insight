import logging
from fastapi import APIRouter, Depends, Query # 👈 쿼리 파라미터 유효성 검사를 위해 Query 추가
from fastapi.responses import JSONResponse

# 🔧 [수정] 필요한 의존성 함수와 스키마를 정확히 임포트
from app.F2_services.graph import GraphService
from app.F5_core.dependencies import get_graph_service
from app.F6_schemas.graph import ExploreGraphResponse, ExploreQuery # 👈 요청 스키마 추가
from app.F6_schemas.base import ErrorResponse, ErrorCode, Message

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/explore", response_model=ExploreGraphResponse, summary="키워드 기반 지식 그래프 탐색", description="입력된 키워드를 중심으로 초기 마인드맵을 구성하는 노드와 엣지 데이터를 반환.")
async def get_initial_graph_for_keyword(
    query: ExploreQuery = Depends(),
    graph_service: GraphService = Depends(get_graph_service) 
):
    """
    키워드 기반의 초기 지식 그래프 데이터를 반환합니다.

    - **keyword**: 탐색의 중심이 될 키워드 (필수)
    """
    # 서비스 레이어를 호출하여 비즈니스 로직 수행
    result = await graph_service.get_initial_graph_by_keyword(query.keyword)

    # 🔧 [패턴 적용] 서비스가 ErrorResponse를 반환하면, 에러 코드에 맞는 상태 코드로 JSON 응답
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 시, 서비스가 반환한 ExploreGraphResponse 객체를 그대로 반환
    return result