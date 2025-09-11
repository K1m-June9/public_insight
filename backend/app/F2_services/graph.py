import logging
from typing import Union

from app.F3_repositories.graph import GraphRepository
from app.F6_schemas.graph import FeedRelationsResponse, FeedRelationsData
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class GraphService:
    """
    그래프 데이터베이스와 관련된 비즈니스 로직을 처리하는 서비스.
    """
    def __init__(self, repo: GraphRepository):
        self.repo = repo

    async def get_related_nodes_for_feed(self, feed_id: int) -> Union[FeedRelationsResponse, ErrorResponse]:
        """
        리포지토리를 통해 피드와 관련된 노드 정보를 조회하고,
        API 응답 스키마에 맞게 데이터를 가공하여 반환함.
        """
        try:
            # 1. 리포지토리를 호출하여 Neo4j로부터 원시 데이터를 가져옴
            graph_data = await self.repo.find_related_nodes_for_feed(feed_id)

            # 2. 결과가 없는 경우 (기준 피드를 찾지 못한 경우) 404 에러를 반환
            if not graph_data:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.FEED_NOT_FOUND
                    )
                )
            
            # 3. Pydantic 스키마를 사용하여 응답 데이터의 유효성을 검증하고 구조를 맞춤
            #    graph_data는 이미 스키마와 거의 동일한 딕셔너리 형태이므로,
            #    FeedRelationsData로 바로 파싱할 수 있음.
            response_data = FeedRelationsData.model_validate(graph_data)

            # 4. 최종 성공 응답 객체를 생성하여 반환
            return FeedRelationsResponse(data=response_data)

        except Exception as e:
            # 리포지토리에서 발생한 예외를 포함한 모든 에러를 처리
            logger.error(f"Error in GraphService for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )