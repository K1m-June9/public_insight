import logging
from typing import Dict, Any, List

# neo4j Session 타입을 명확히 하기 위해 임포트
from neo4j import AsyncDriver
from app.F14_knowledge_graph.graph_ml import predict_similar_nodes
from app.F7_models.feeds import ContentTypeEnum

logger = logging.getLogger(__name__)

class GraphRepository:
    """
    Neo4j 데이터베이스와의 통신을 책임지는 리포지토리.
    - 주입된 AsyncDriver 사용하여 Cypher 쿼리를 실행함.
    """
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def find_initial_nodes_by_keyword(self, keyword: str) -> Dict[str, Any] | None:
        """
        [ML + Cypher 하이브리드 방식으로 수정됨]
        ML로 유사 피드를 예측하고, 예측된 피드와 관련된 기관을 Cypher로 조회.
        """
        try:
            # 1. ML 모델을 호출하여 유사 노드 ID 목록을 예측 (피드 위주로)
            start_node_id = f"keyword_{keyword}"
            # 넉넉하게 상위 20개의 유사 노드를 후보로 가져옴
            predicted_nodes = predict_similar_nodes(start_node_id, top_n=20)

            if not predicted_nodes:
                return None
            
            # 예측 결과에서 '피드' 노드의 ID만 필터링하고, 실제 DB ID(숫자)만 추출
            predicted_feed_db_ids = [
                int(node_id.split('_')[1]) 
                for node_id, similarity in predicted_nodes 
                if node_id.startswith('feed_')
            ]

            if not predicted_feed_db_ids:
                return None

            # 2. [핵심 수정] 예측된 피드 ID들을 사용하여, 해당 피드들과 관련 기관 정보를 한번에 조회
            #    이제 쿼리는 '탐색'이 아닌, 예측 결과를 '보강'하는 역할을 함
            cypher_query = """
            // 1. 추천된 피드 ID 리스트를 파라미터로 받음
            UNWIND $feed_ids as feed_id
            MATCH (f:Feed {id: feed_id})
            
            // 2. 각 피드와 연결된 기관을 찾음
            MATCH (o:Organization)-[:PUBLISHED]->(f)
            
            // 3. 찾은 모든 피드와 기관들을 중복 없이 집계하여 반환
            RETURN
                collect(DISTINCT f { .*, content_type: toString(f.content_type) }) AS feeds,
                collect(DISTINCT o { .* }) AS organizations
            """
            
            async with self.driver.session() as session:
                result = await session.run(cypher_query, feed_ids=predicted_feed_db_ids)
                record = await result.single()

            if not record:
                return None
                
            # 3. 조회된 결과를 기존 메서드의 반환 형식과 동일하게 '재조립'
            final_result = {
                "keyword": {"id": keyword, "name": keyword},
                "feeds": record.data().get("feeds", []),
                "organizations": record.data().get("organizations", [])
            }
            
            return final_result

        except Exception as e:
            logger.error(f"Error finding ML-based nodes for keyword '{keyword}': {e}", exc_info=True)
            raise

    async def expand_from_feed(
        self, feed_id: int, exclude_ids: set[str]
    ) -> Dict[str, Any] | None:
        """
        [ML] 피드 노드에서 확장.
        - ML로 유사 노드(피드, 키워드)를 예측하고, Cypher로 소속 기관을 확정적으로 조회.
        """
        try:
            start_node_id = f"feed_{feed_id}"
            
            # 1. ML 모델로 유사 노드 예측 (상위 20개 후보)
            predicted_nodes = predict_similar_nodes(
                start_node_id, top_n=20, exclude_ids=exclude_ids
            )
            
            # 2. Cypher로 '소속 기관' 정보는 확정적으로 조회
            cypher_query = """
            MATCH (f:Feed {id: $feed_id})<-[:PUBLISHED]-(o:Organization)
            RETURN o { .id, .name } AS organization
            """
            async with self.driver.session() as session:
                result = await session.run(cypher_query, feed_id=feed_id)
                record = await result.single()
            
            org_data = record.data().get("organization") if record else None
            
            # 3. 예측 결과와 조회 결과를 하나의 딕셔너리로 통합하여 반환
            return {
                "predicted_nodes": predicted_nodes,
                "explicit_nodes": {
                    "organization": org_data
                }
            }
        except Exception as e:
            logger.error(f"Error expanding from feed '{feed_id}': {e}", exc_info=True)
            raise


    async def expand_from_organization(
        self, org_id: int, exclude_ids: set[str]
    ) -> Dict[str, Any] | None:
        """
        [ML] 기관 노드에서 확장.
        - ML로 기관과 문맥적으로 유사한 대표 피드와 핵심 키워드를 예측.
        """
        try:
            start_node_id = f"organization_{org_id}"
            predicted_nodes = predict_similar_nodes(
                start_node_id, top_n=20, exclude_ids=exclude_ids
            )
            
            return {"predicted_nodes": predicted_nodes}
        except Exception as e:
            logger.error(f"Error expanding from organization '{org_id}': {e}", exc_info=True)
            raise


    async def expand_from_keyword(
        self, keyword: str, exclude_ids: set[str]
    ) -> Dict[str, Any] | None:
        """
        [ML] 키워드 노드에서 확장.
        - ML로 관련 피드, 유사 키워드를 예측하고, 예측된 피드의 소속 기관을 조회.
        """
        try:
            start_node_id = f"keyword_{keyword}"
            predicted_nodes = predict_similar_nodes(
                start_node_id, top_n=20, exclude_ids=exclude_ids
            )
            if not predicted_nodes: return None
            
            # 예측된 노드 중 '피드' 타입의 실제 DB ID만 추출
            predicted_feed_db_ids = [
                int(node_id.split('_')[1]) 
                for node_id, sim in predicted_nodes if node_id.startswith('feed_')
            ]

            organizations = []
            if predicted_feed_db_ids:
                # 예측된 피드들의 소속 기관 정보를 Cypher로 조회
                cypher_query = """
                UNWIND $feed_ids as feed_id
                MATCH (f:Feed {id: feed_id})<-[:PUBLISHED]-(o:Organization)
                RETURN DISTINCT o { .id, .name } AS organization
                """
                async with self.driver.session() as session:
                    result = await session.run(cypher_query, feed_ids=predicted_feed_db_ids)
                    organizations = [record.data()['organization'] async for record in result]

            return {
                "predicted_nodes": predicted_nodes,
                "explicit_nodes": {
                    "organizations": organizations
                }
            }
        except Exception as e:
            logger.error(f"Error expanding from keyword '{keyword}': {e}", exc_info=True)
            raise

    # 아아.. 아아....아아아아아아아아...
    # organization 도메인에서 워드클라우드 또 삭제해야하는데
    # 프론트엔드도 바꿔야하네
    # 앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜앜
    async def get_keywords_by_popularity(
        self, organization_name: str | None, limit: int
    ) -> List[Dict[str, Any]]:
        """
        인기 점수를 기준으로 키워드 목록을 조회함.
        - organization_name이 있으면 해당 기관으로 범위를 좁힘.
        - 없으면 전체 키워드를 대상으로 함.
        """
        # [핵심] '인기 점수' 계산 로직:
        # (CONTAINS_KEYWORD 관계의 score 합계) + (SEARCHED 관계 수 * 가중치 1.5)
        # 검색 행동에 더 높은 가중치를 부여하여 사용자 트렌드를 반영함.
        popularity_score_logic = "(sum(r.score) * 1.0) + (count(u) * 1.5)"

        if organization_name:
            # --- 기관별 키워드 쿼리 ---
            # 기관 이름(name)을 기준으로 필터링함.
            cypher_query = f"""
                MATCH (o:Organization {{name: $org_name}})-[:PUBLISHED]->(f:Feed)
                MATCH (f)-[r:CONTAINS_KEYWORD]->(k:Keyword)
                OPTIONAL MATCH (k)<-[:SEARCHED]-(u:User)
                RETURN k.name AS text, {popularity_score_logic} AS value
                ORDER BY value DESC
                LIMIT $limit
            """
            params = {"org_name": organization_name, "limit": limit}
        else:
            # --- 전체 키워드 쿼리 ---
            cypher_query = f"""
                MATCH (f:Feed)-[r:CONTAINS_KEYWORD]->(k:Keyword)
                OPTIONAL MATCH (k)<-[:SEARCHED]-(u:User)
                RETURN k.name AS text, {popularity_score_logic} AS value
                ORDER BY value DESC
                LIMIT $limit
            """
            params = {"limit": limit}

        try:
            async with self.driver.session() as session:
                result = await session.run(cypher_query, **params)
                return [record.data() async for record in result]
        except Exception as e:
            logger.error(f"Error getting keywords by popularity: {e}", exc_info=True)
            raise