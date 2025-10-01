import logging
from fastapi import APIRouter, Depends, Query, Path
from fastapi.responses import JSONResponse

from app.F2_services.graph import GraphService
from app.F5_core.dependencies import get_graph_service
from app.F6_schemas.graph import ExploreGraphResponse, ExploreQuery, ExpandQuery, WordCloudResponse, RelatedKeywordsResponse
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
    result = await graph_service.get_initial_graph_by_keyword(query.keyword)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/expand", response_model=ExploreGraphResponse, summary="지식 그래프 노드 확장", description="특정 노드를 중심으로 연결된 다음 단계의 노드와 엣지 데이터를 반환.")
async def get_expanded_graph_from_node(
    node_id: str = Query(..., description='확장할 노드의 고유 ID (예: "feed_123")'),
    node_type: str = Query(..., description='확장할 노드의 종류 (예: "feed")'),
    exclude_ids: str | None = Query(None, description="추천에서 제외할 노드 ID 목록 (쉼표로 구분)"),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    특정 노드를 클릭했을 때, 연결된 다음 단계의 노드와 관계를 반환하여 마인드맵을 확장.

    - **node_id**: 확장할 노드의 고유 ID (필수)
    - **node_type**: 확장할 노드의 종류 (필수)
    - **exclude_ids**: (선택) 이미 화면에 표시된 노드 ID들을 쉼표로 구분하여 전달.
    """
    # 서비스 레이어의 확장 메서드에 모든 파라미터를 전달하여 호출
    result = await graph_service.get_expanded_graph_by_node(
        node_id=node_id, 
        node_type=node_type,
        exclude_ids_str=exclude_ids
    )

    # 에러 처리 패턴은 동일
    if isinstance(result, ErrorResponse):
        status_code = 400 if result.error.code == ErrorCode.BAD_REQUEST else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result

@router.get("/wordcloud", response_model=WordCloudResponse, summary="인기 키워드/워드클라우드 데이터 조회", description="전체 또는 특정 기관의 인기 키워드 목록을 점수와 함께 반환.")
async def get_wordcloud(
    # 쿼리 파라미터로 organization_name과 limit을 받음
    organization_name: str | None = Query(None, description="데이터를 필터링할 기관의 이름"),
    limit: int = Query(30, ge=1, le=50, description="반환할 최대 키워드 개수"),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    메인 페이지의 '인기 키워드' 또는 기관 페이지의 '워드클라우드'를 위한 데이터를 제공

    - **organization_name**: (선택) 특정 기관의 데이터로 제한하려면 기관 이름을 입력
    - **limit**: (선택) 반환할 최대 키워드 개수를 지정합니다. (기본값: 30, 최소: 1, 최대: 50)
    """
    # 서비스 레이어의 워드클라우드 데이터 조회 메서드를 호출
    result = await graph_service.get_wordcloud_data(organization_name, limit)
    
    # 에러 처리 패턴은 다른 API들과 완벽하게 동일함
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
        
    return result

@router.get("/feeds/{feed_id}/related-keywords", response_model=RelatedKeywordsResponse, summary="피드 상세 페이지의 연관 키워드 조회 (ML 기반)", description="특정 피드와 유사한 키워드 목록을 연관도 점수와 함께 반환.")
async def get_related_keywords_for_feed(
    # 경로 파라미터 유효성 검사: feed_id는 0보다 큰 정수여야 함
    feed_id: int = Path(..., gt=0, description="관련 키워드를 조회할 피드의 ID"),
    limit: int = Query(10, ge=5, le=15, description="반환할 최대 키워드 개수"),
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    피드 상세 페이지 우측의 '관련 토픽' 섹션에 사용될 데이터를 제공.

    - **feed_id**: (필수) 대상 피드의 고유 ID.
    - **limit**: (선택) 반환할 키워드 개수 (기본값: 10, 최소: 5, 최대: 15).
    """
    # 서비스 레이어의 새로운 메서드를 호출
    result = await graph_service.get_related_keywords_for_feed(feed_id, limit)
    
    # 에러 처리 패턴은 다른 API들과 완벽하게 동일함
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
        
    return result