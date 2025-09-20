import logging
from typing import Union

from app.F3_repositories.graph import GraphRepository
# 🔧 [수정] 우리 프로젝트의 스키마들을 임포트
from app.F6_schemas.graph import (
    ExploreGraphResponse, 
    ExploreGraphData, 
    GraphNode, 
    GraphEdge
)
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class GraphService:
    """
    그래프 데이터베이스와 관련된 비즈니스 로직을 처리하는 서비스.
    - 리포지토리로부터 받은 데이터를 API 응답 스키마에 맞게 가공하고 변환함.
    """
    def __init__(self, repo: GraphRepository):
        self.repo = repo

    async def get_initial_graph_by_keyword(
        self, keyword: str
    ) -> Union[ExploreGraphResponse, ErrorResponse]:
        """
        키워드를 기반으로 마인드맵 초기 그래프 데이터를 조회하고 구조화함.
        """
        try:
            # 1. 리포지토리를 호출하여 Neo4j로부터 원시 데이터를 가져옴
            raw_graph_data = await self.repo.find_initial_nodes_by_keyword(keyword)

            # 2. 결과가 없는 경우 (리포지토리가 None을 반환한 경우)
            if not raw_graph_data:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=f"키워드 '{keyword}'와 관련된 데이터를 찾을 수 없습니다."
                    )
                )

            # 3. 원시 데이터를 nodes와 edges 리스트로 '재조립'
            nodes, edges = self._structure_for_frontend(raw_graph_data)

            # 4. 최종 성공 응답 스키마에 데이터를 담아 생성
            response_data = ExploreGraphData(nodes=nodes, edges=edges)
            
            return ExploreGraphResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error in GraphService for keyword '{keyword}': {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
            
    def _structure_for_frontend(self, raw_data: dict) -> tuple[list[GraphNode], list[GraphEdge]]:
        """
        (Helper) 리포지토리에서 받은 데이터를 프론트엔드 스키마에 맞게 변환함.
        """
        nodes = []
        edges = []
        
        # --- 중앙 키워드 노드 생성 ---
        keyword_node_data = raw_data.get('keyword', {})
        if not keyword_node_data: # 키워드가 없는 경우는 거의 없지만, 방어 코드
            return [], []
            
        keyword_id = f"keyword_{keyword_node_data['id']}"
        nodes.append(GraphNode(
            id=keyword_id,
            type='keyword',
            label=keyword_node_data['name'],
        ))

        # --- 관련 피드 노드 및 관계 생성 ---
        for feed in raw_data.get('feeds', []):
            feed_id = f"feed_{feed['id']}"
            nodes.append(GraphNode(
                id=feed_id,
                type='feed',
                label=feed['title'],
                metadata={
                    'published_date': str(feed.get('published_date'))
                }
            ))
            # (Feed)-[:CONTAINS_KEYWORD]->(Keyword) 관계를 엣지로 추가
            edges.append(GraphEdge(
                id=f"{feed_id}-CONTAINS-{keyword_id}",
                source=feed_id,
                target=keyword_id,
                label='포함'
            ))

        # --- 관련 기관 노드 및 관계 생성 ---
        # 피드 데이터에서 어떤 기관이 어떤 피드를 발행했는지 역추적
        feeds_by_org = {}
        for feed in raw_data.get('feeds', []):
            org_id = feed.get('organization_id')
            if org_id:
                if org_id not in feeds_by_org:
                    feeds_by_org[org_id] = []
                feeds_by_org[org_id].append(feed['id'])

        for org in raw_data.get('organizations', []):
            org_id_numeric = org['id']
            org_id_str = f"organization_{org_id_numeric}"
            nodes.append(GraphNode(
                id=org_id_str,
                type='organization',
                label=org['name']
            ))
            
            # (Organization)-[:PUBLISHED]->(Feed) 관계를 엣지로 추가
            for feed_id_numeric in feeds_by_org.get(org_id_numeric, []):
                feed_id_str = f"feed_{feed_id_numeric}"
                edges.append(GraphEdge(
                    id=f"{org_id_str}-PUBLISHED-{feed_id_str}",
                    source=org_id_str,
                    target=feed_id_str,
                    label='발행'
                ))
                
        return nodes, edges
        
