# ============================================================================
# PoC를 위한 파일: 테스트 용도
# ============================================================================

import logging
from typing import Dict, Any
from neo4j import AsyncDriver # F5_core/dependencies.py에서 사용한 타입 힌트와 일치

logger = logging.getLogger(__name__)

class GraphRepository:
    """
    Neo4j 데이터베이스와의 통신을 책임지는 리포지토리.
    Cypher 쿼리를 실행하고 결과를 반환함.
    """
    def __init__(self, driver: AsyncDriver):
        self.driver = driver

    async def find_related_nodes_for_feed(self, feed_id: int) -> Dict[str, Any]:
        """
        특정 피드 ID와 직접적으로 연결된 모든 노드 정보를 조회함.
        하나의 복잡한 Cypher 쿼리로 모든 관계를 한 번에 가져옴.
        """
        # 💥 이것이 바로 그래프 데이터베이스의 힘을 보여주는 Cypher 쿼리임.
        cypher_query = """
        // 1. 기준이 되는 피드 노드를 찾음 (MATCH)
        MATCH (source_feed:Feed {id: $feed_id})
        
        // 2. 이 피드와 연결된 이웃 노드들을 선택적으로(OPTIONAL) 찾음
        // OPTIONAL MATCH는 관계가 존재하지 않더라도 쿼리가 실패하지 않도록 함
        OPTIONAL MATCH (source_feed)<-[:PUBLISHED]-(organization:Organization)
        OPTIONAL MATCH (source_feed)-[:BELONGS_TO]->(category:Category)
        OPTIONAL MATCH (source_feed)<-[:BOOKMARKED]-(bookmarked_user:User)
        OPTIONAL MATCH (source_feed)<-[:RATED]-(rated_user:User)

        // 3. 찾은 모든 정보를 반환(RETURN)함
        RETURN
            // source_feed 노드의 id와 title을 딕셔너리 형태로 반환
            source_feed { .id, .title } AS source_feed,
            // organization 노드의 id와 name을 반환 (없으면 null)
            organization { .id, .name } AS published_by,
            // category 노드의 id와 name을 반환 (없으면 null)
            category { .id, .name } AS belongs_to,
            // 이 피드를 북마크한 모든 사용자 노드의 리스트를 반환
            collect(DISTINCT bookmarked_user { .id, .user_id, .nickname }) AS bookmarked_by_users,
            // 이 피드에 평점을 남긴 모든 사용자 노드의 리스트를 반환
            collect(DISTINCT rated_user { .id, .user_id, .nickname }) AS rated_by_users
        """
        try:
            # 💥 driver.execute_query를 사용하여 쿼리를 실행하도록 수정합니다.
            records, summary, keys = await self.driver.execute_query(
                cypher_query, feed_id=feed_id, database_="neo4j"
            )
            
            if records:
                # execute_query는 record 리스트를 반환하므로, 첫 번째 결과를 가져옴
                return records[0].data()
            else:
                return None

        except Exception as e:
            logger.error(f"Error finding related nodes for feed_id {feed_id} in Neo4j: {e}", exc_info=True)
            raise