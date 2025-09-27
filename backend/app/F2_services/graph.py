import logging
import math
from typing import Union, Dict, Any, List

from app.F3_repositories.graph import GraphRepository
# 🔧 [수정] 우리 프로젝트의 스키마들을 임포트
from app.F6_schemas.graph import (
    ExploreGraphResponse, 
    ExploreGraphData, 
    GraphNode, 
    GraphEdge,
    WordCloudItem,
    WordCloudResponse,
    RelatedKeywordItem,
    RelatedKeywordsResponse
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
        - 노드의 초기 위치(x, y)와 부가 정보(메타데이터)를 계산하여 포함함.
        - 초기 화면에서는 중심 키워드와 1차 연결된 노드/엣지만 생성함.
        """
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        
        # --- 1. 중심 키워드 노드 생성 ---
        keyword_node_data = raw_data.get('keyword')
        if not keyword_node_data:
            return [], []
            
        keyword_id_str = f"keyword_{keyword_node_data['name']}"
        
        keyword_node = GraphNode(
            id=keyword_id_str,
            type='keyword',
            label=keyword_node_data['name'],
            metadata={} # 좌표는 나중에 프론트엔드에서 계산하므로 비워둠
        )
        nodes.append(keyword_node)

        # --- 2. 관련 피드 및 기관 노드 생성 ---
        # 피드와 기관 데이터를 미리 딕셔너리로 만들어두면 조회가 빠름
        feeds_map = {feed['id']: feed for feed in raw_data.get('feeds', [])}
        orgs_map = {org['id']: org for org in raw_data.get('organizations', [])}

        # 피드 노드 생성
        for feed_id, feed_data in feeds_map.items():
            nodes.append(GraphNode(
                id=f"feed_{feed_id}",
                type='feed',
                label=feed_data['title'],
                metadata={
                    # 우리가 논의했던 모든 부가 정보를 metadata에 추가
                    'published_date': str(feed_data.get('published_date')),
                    'view_count': feed_data.get('view_count'),
                    'avg_rating': feed_data.get('average_rating'),
                    'bookmark_count': feed_data.get('bookmark_count')
                }
            ))
        
        # 기관 노드 생성
        for org_id, org_data in orgs_map.items():
            nodes.append(GraphNode(
                id=f"organization_{org_id}",
                type='organization',
                label=org_data['name'],
                metadata={}
            ))
            
        # --- 3. 1단계 엣지(관계) 생성 ---
        # 노트북LM 스타일을 위해, 초기 화면에서는 중심 키워드와 다른 노드들을 잇는 엣지만 생성함.
        for node in nodes:
            # 🔧 [수정] 객체의 속성에 접근할 때는 '.'을 사용
            # 자기 자신이 아니고, 중심 노드(keyword_node)가 아닌 노드들만 연결
            if node.id != keyword_node.id:
                edges.append(GraphEdge(
                    id=f"{keyword_node.id}-INITIAL_LINK-{node.id}",
                    source=keyword_node.id, # 모든 엣지는 중심 키워드에서 시작
                    target=node.id,
                ))
                
        return nodes, edges
        
    async def get_expanded_graph_by_node(
        self, node_id: str, node_type: str,
        exclude_ids_str: str | None = None
    ) -> Union[ExploreGraphResponse, ErrorResponse]:
        """
        [ML 기반으로 리팩토링됨]
        클릭된 노드를 중심으로 그래프를 확장하고, 비즈니스 규칙에 따라 결과를 필터링함.
        """
        try:
            entity_id = node_id.split('_', 1)[-1]
            exclude_ids = set(exclude_ids_str.split(',')) if exclude_ids_str else set()

            raw_expansion_data: Dict[str, Any] | None = None
            rules: Dict[str, int] = {}

            if node_type == 'feed':
                raw_expansion_data = await self.repo.expand_from_feed(int(entity_id), exclude_ids)
                rules = {'feed': 4, 'keyword': 3, 'organization': 1}
            
            elif node_type == 'organization':
                raw_expansion_data = await self.repo.expand_from_organization(int(entity_id), exclude_ids)
                rules = {'feed': 4, 'keyword': 3}
            
            elif node_type == 'keyword':
                raw_expansion_data = await self.repo.expand_from_keyword(str(entity_id), exclude_ids)
                rules = {'feed': 4, 'keyword': 2, 'organization': 1}
            
            else:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.BAD_REQUEST, message="지원하지 않는 노드 타입입니다."))

            if not raw_expansion_data:
                return ExploreGraphResponse(success=True, data=ExploreGraphData(nodes=[], edges=[]))
            
            final_node_infos = self._filter_and_select_nodes(raw_expansion_data, rules, exclude_ids)
            
            # [핵심 수정 1] 리포지토리에서 온 'predicted_details'를 변수로 추출합니다.
            predicted_details = raw_expansion_data.get("predicted_details", {})
            
            # [핵심 수정 2] 추출한 'predicted_details'를 헬퍼 함수에 인자로 전달합니다.
            nodes, edges = self._structure_expansion_for_frontend(
                node_id, final_node_infos, predicted_details
            )
            
            response_data = ExploreGraphData(nodes=nodes, edges=edges)
            return ExploreGraphResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error expanding graph for node '{node_id}': {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))

    def _filter_and_select_nodes(
        self, 
        raw_data: Dict[str, Any], 
        rules: Dict[str, int],
        exclude_ids: set[str]
    ) -> List[Dict[str, Any]]:
        """
        (Helper) ML 예측 결과와 비즈니스 규칙에 따라 최종 노드를 선별함.
        - [수정] 상세 정보가 있는 노드가 예측만 있는 노드를 덮어쓸 수 있도록 로직 변경
        """
        selected_nodes_map: Dict[str, Dict[str, Any]] = {}
        counts = {node_type: 0 for node_type in rules.keys()}
        
        # 1. 예측된 노드들부터 규칙에 따라 '자리'를 채워넣기 (상세 정보는 아직 없음)
        for node_id, similarity in raw_data.get("predicted_nodes", []):
            node_type = node_id.split('_')[0]
            
            if node_type in rules and counts[node_type] < rules[node_type] and node_id not in exclude_ids:
                selected_nodes_map[node_id] = {'id': node_id, 'type': node_type, 'similarity': similarity}
                counts[node_type] += 1

        # 2. Cypher로 확정적으로 가져온 노드(기관 등)로 '정보를 보강'하거나 '새로 추가'
        explicit_nodes = raw_data.get("explicit_nodes", {})
        for node_type, node_or_list in explicit_nodes.items():
            node_type_singular = node_type.rstrip('s') 
            
            if node_type_singular in rules:
                nodes_to_process = node_or_list if isinstance(node_or_list, list) else [node_or_list]
                
                for node_data in nodes_to_process:
                    if not node_data: continue
                    
                    node_id = f"{node_type_singular}_{node_data['id']}"
                    
                    # [핵심 수정] 
                    # 이미 맵에 예측 노드(자리만 있는)가 있더라도, 상세 정보가 있는 현재 노드가
                    # 그 자리를 덮어쓰도록 'and node_id not in selected_nodes_map' 조건을 제거합니다.
                    # 단, 할당량(counts)과 제외 목록(exclude_ids) 체크는 여전히 유지합니다.
                    if counts[node_type_singular] < rules[node_type_singular] and node_id not in exclude_ids:
                        
                        # 만약 이 노드가 예측 목록에 없던 새로운 노드라면, 카운트를 증가시킵니다.
                        if node_id not in selected_nodes_map:
                            counts[node_type_singular] += 1
                        
                        # 예측만 있던 노드를 상세 정보가 있는 노드로 덮어쓰거나, 새로 추가합니다.
                        selected_nodes_map[node_id] = {'id': node_id, 'type': node_type_singular, 'data': node_data}

        return list(selected_nodes_map.values())

    def _structure_expansion_for_frontend(
        self, start_node_id: str, final_node_infos: List[Dict[str, Any]],
        # [핵심 수정 3] 'predicted_details'를 받을 수 있도록 파라미터 추가
        details_map: Dict[str, Any]
    ) -> tuple[List[GraphNode], List[GraphEdge]]:
        """
        (Helper) 최종 선별된 노드 정보 목록을 프론트엔드 스키마에 맞게 변환함.
        """
        nodes = []
        edges = []
        
        for item in final_node_infos:
            node_id = item['id']
            generic_type = item['type']
            
            # [핵심 수정 4]
            # 'item' 자체의 'data'가 아닌, 파라미터로 받은 'details_map'에서 상세 정보를 조회합니다.
            # 이것이 모든 예측된 노드(feed, keyword, organization)의 이름을 찾을 수 있게 해줍니다.
            node_data_from_details = details_map.get(node_id)
            node_data_from_item = item.get('data')

            # 상세 정보가 있으면 사용하고, 없으면 ID에서 라벨을 유추합니다.
            # details_map에 있는 정보가 더 우선순위가 높습니다.
            node_data = node_data_from_details or node_data_from_item
            label = node_data.get('title', node_data.get('name')) if node_data else node_id.split('_', 1)[-1]
            
            nodes.append(GraphNode(
                id=node_id,
                type=generic_type,
                label=label,
                metadata={}
            ))

            edges.append(GraphEdge(
                id=f"{start_node_id}-EXPANDS_TO-{node_id}",
                source=start_node_id,
                target=node_id
            ))

        return nodes, edges
    
    # 새로 만드는거긴한데 정말 눈물이 난다.
    async def get_wordcloud_data(
        self, organization_name: str | None, limit: int
    ) -> Union[WordCloudResponse, ErrorResponse]:
        """
        워드클라우드 또는 인기 키워드 목록을 위한 데이터를 조회하고 구조화함.
        """
        try:
            # 1. 리포지토리를 호출하여 Neo4j로부터 원시 데이터를 가져옴
            keywords_data = await self.repo.get_keywords_by_popularity(organization_name, limit)
            
            # 2. Pydantic 스키마를 사용하여 응답 데이터의 유효성을 검증하고 구조를 맞춤.
            #    데이터가 없는 경우(keywords_data가 빈 리스트인 경우)에도 
            #    Pydantic이 알아서 처리하여 빈 리스트를 가진 성공 응답을 만들어 줌.
            response_data = [WordCloudItem(**item) for item in keywords_data]
            
            # 3. 최종 성공 응답 객체를 생성하여 반환
            return WordCloudResponse(success=True, data=response_data)

        except Exception as e:
            # 리포지토리에서 발생한 예외를 포함한 모든 에러를 처리
            logger.error(f"Error in get_wordcloud_data service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    async def get_related_keywords_for_feed(
        self, feed_id: int, limit: int = 10
    ) -> Union[RelatedKeywordsResponse, ErrorResponse]:
        """
        특정 피드와 연관된 키워드 목록을 ML 모델을 통해 조회하고 구조화함.
        """
        try:
            # 1. 리포지토리를 호출하여 (키워드, 유사도) 튜플 리스트를 가져옴
            similar_keywords = await self.repo.get_similar_keywords_for_feed(feed_id, limit)
            
            # 2. [핵심 비즈니스 로직]
            #    - 각 키워드의 유사도(0.0 ~ 1.0)를 연관도 점수(0 ~ 100)로 변환
            #    - Pydantic 스키마(RelatedKeywordItem) 객체 리스트로 재조립
            response_data = [
                RelatedKeywordItem(
                    text=keyword,
                    score=int(similarity * 100) # 👈 0.98 -> 98점으로 변환
                ) 
                for keyword, similarity in similar_keywords
            ]
            
            # 3. 최종 성공 응답 객체를 생성하여 반환
            return RelatedKeywordsResponse(success=True, data=response_data)

        except Exception as e:
            # 리포지토리에서 발생한 예외를 포함한 모든 에러를 처리
            logger.error(f"Error getting related keywords for feed '{feed_id}': {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )