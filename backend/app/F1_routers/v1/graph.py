import logging
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.F2_services.graph import GraphService
from app.F5_core.dependencies import get_graph_service
from app.F6_schemas.graph import ExploreGraphResponse, ExploreQuery, ExpandQuery
from app.F6_schemas.base import ErrorResponse, ErrorCode, Message

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/explore", response_model=ExploreGraphResponse, summary="키워드 기반 지식 그래프 탐색", description="입력된 키워드를 중심으로 초기 마인드맵을 구성하는 노드와 엣지 데이터를 반환.")
async def get_initial_graph_for_keyword(
    query: ExploreQuery = Depends(),
    graph_service: GraphService = Depends(get_graph_service) 
):
    """
    키워드 기반의 초기 지식 그래프 데이터를 반환

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

@router.get("/expand", response_model=ExploreGraphResponse, summary="지식 그래프 노드 확장", description="특정 노드를 중심으로 연결된 다음 단계의 노드와 엣지 데이터를 반환합니다.")
async def get_expanded_graph_from_node(
    # 🔧 [수정] ExpandQuery 스키마를 사용하여 node_id와 node_type을 받음
    query: ExpandQuery = Depends(),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    특정 노드를 클릭했을 때, 연결된 다음 단계의 노드와 관계를 반환하여 마인드맵을 확장

    - **node_id**: 확장할 노드의 고유 ID (예: "feed_123")
    - **node_type**: 확장할 노드의 종류 (예: "feed", "organization", "keyword")
    """
    # 서비스 레이어의 새로운 확장 메서드를 호출
    result = await graph_service.get_expanded_graph_by_node(
        node_id=query.node_id, 
        node_type=query.node_type
    )

    # 에러 처리 패턴은 /explore와 완벽하게 동일함
    if isinstance(result, ErrorResponse):
        status_code = 400 if result.error.code == ErrorCode.BAD_REQUEST else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result