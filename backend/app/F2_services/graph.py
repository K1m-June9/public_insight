import logging
from typing import Union, Dict, Any, List

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
        
    async def get_expanded_graph_by_node(
        self, node_id: str, node_type: str
    ) -> Union[ExploreGraphResponse, ErrorResponse]:
        """
        클릭된 노드를 중심으로 그래프를 확장함.
        - node_type에 따라 적절한 리포지토리 메서드를 호출하고 결과를 구조화함.
        """
        try:
            # 1. node_type에 따라 어떤 리포지토리 메서드를 호출할지 결정
            raw_expansion_data: List[Dict[str, Any]] | None = None
            # node_id에서 접두사(예: "feed_")를 제거하여 순수한 숫자/문자 ID를 추출
            # 💥 중요: 이 ID 추출 방식은 프론트엔드에서 ID를 생성하는 규칙과 일치해야 함
            entity_id = node_id.split('_', 1)[-1]

            if node_type == 'feed':
                raw_expansion_data = await self.repo.expand_from_feed(int(entity_id))
            elif node_type == 'organization':
                raw_expansion_data = await self.repo.expand_from_organization(int(entity_id))
            elif node_type == 'keyword':
                raw_expansion_data = await self.repo.expand_from_keyword(str(entity_id))
            else:
                # 지원하지 않는 노드 타입인 경우 에러 반환
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.BAD_REQUEST, message="지원하지 않는 노드 타입입니다."))

            # 2. 리포지토리 결과가 없는 경우 (확장할 노드가 없는 경우)
            if not raw_expansion_data:
                # 빈 데이터를 성공적으로 반환 (에러가 아님)
                return ExploreGraphResponse(success=True, data=ExploreGraphData(nodes=[], edges=[]))
            
            # 3. 원시 데이터를 프론트엔드용 nodes와 edges로 '재조립'
            nodes, edges = self._structure_expansion_for_frontend(node_id, raw_expansion_data)
            
            # 4. 최종 성공 응답 반환
            response_data = ExploreGraphData(nodes=nodes, edges=edges)
            return ExploreGraphResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error expanding graph for node '{node_id}': {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))


    def _structure_expansion_for_frontend(
        self, start_node_id: str, raw_data: List[Dict[str, Any]]
    ) -> tuple[List[GraphNode], List[GraphEdge]]:
        """ (Helper) 리포지토리의 확장 결과를 프론트엔드 스키마에 맞게 변환함. """
        nodes = []
        edges = []
        
        for item in raw_data:
            node_data = item.get('node')
            node_type_from_db = item.get('type') # 예: 'similar_feed', 'major_keyword'
            
            if not node_data:
                continue

            # DB에서 온 node_type을 프론트엔드에서 사용할 일반 타입으로 변환
            # 예: 'similar_feed', 'recommended_feed' -> 'feed'
            generic_type = node_type_from_db.split('_')[-1] #_
            
            # 노드 ID 생성 (접두사 + 실제 ID)
            # Keyword 노드는 name이 id 역할을 함
            node_id = f"{generic_type}_{node_data.get('name', node_data.get('id'))}"
            
            # 이미 생성된 노드는 추가하지 않도록 중복 체크 (선택적이지만 안정성을 높임)
            if not any(n.id == node_id for n in nodes):
                nodes.append(GraphNode(
                    id=node_id,
                    type=generic_type,
                    label=node_data.get('title', node_data.get('name')),
                    # TODO: 필요에 따라 metadata 추가 (예: 피드의 발행일 등)
                    metadata={} 
                ))

            # 엣지(관계) 생성
            # 시작 노드(클릭된 노드)와 새로 찾은 노드를 연결
            edges.append(GraphEdge(
                id=f"{start_node_id}-EXPANDS_TO-{node_id}",
                source=start_node_id,
                target=node_id,
                label=node_type_from_db # 관계 라벨에 구체적인 타입(예: '유사 피드')을 넣어주면 더 풍부한 정보 제공 가능
            ))

        return nodes, edges