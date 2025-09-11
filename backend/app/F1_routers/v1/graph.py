import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.F2_services.graph import GraphService
from app.F5_core.dependencies import get_graph_service # 👈 방금 만든 의존성 함수 import
from app.F6_schemas.graph import FeedRelationsResponse
from app.F6_schemas.base import ErrorResponse, ErrorCode, Message

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/feeds/{feed_id}/related", response_model=FeedRelationsResponse)
async def get_feed_relations(
    feed_id: int,
    # 👇 MySQL 서비스와 똑같은 방식으로 서비스를 주입받음
    graph_service: GraphService = Depends(get_graph_service) 
):
    """특정 피드와 직접적으로 연결된 모든 노드(관계) 정보를 반환함."""
    result = await graph_service.get_related_nodes_for_feed(feed_id)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result