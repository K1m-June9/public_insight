import logging
from typing import Dict, Any

# neo4j Session 타입을 명확히 하기 위해 임포트
from neo4j import AsyncDriver

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
        특정 키워드를 중심으로, 마인드맵 초기 화면에 필요한 노드들을 조회함.
        - 하나의 Cypher 쿼리로 중앙 키워드, 관련 피드, 관련 기관을 모두 가져옴.
        - 반환값: {'keyword': {...}, 'feeds': [...], 'organizations': [...]} 형태의 딕셔너리
        """
        # [핵심] 키워드와 관련된 정보를 집계(collect)하는 Cypher 쿼리
        cypher_query = """
        // 1. 입력받은 $keyword와 일치하는 :Keyword 노드를 찾음
        MATCH (k:Keyword {name: $keyword})

        // 2. 이 키워드와 :CONTAINS_KEYWORD 관계로 연결된 :Feed 노드들을 찾음 (선택적)
        //    - OPTIONAL MATCH: 관련 피드가 없더라도 쿼리가 실패하지 않음
        OPTIONAL MATCH (f:Feed)-[:CONTAINS_KEYWORD]->(k)

        // 3. 위에서 찾은 각 피드와 :PUBLISHED 관계로 연결된 :Organization 노드를 찾음 (선택적)
        OPTIONAL MATCH (o:Organization)-[:PUBLISHED]->(f)

        // 4. 찾은 모든 정보를 집계하여 반환
        RETURN
            // 중앙 키워드 노드의 속성을 'keyword'라는 이름으로 반환
            k { .id, .name } AS keyword,
            
            // 중복을 제거(DISTINCT)하여 관련 피드 노드들의 리스트를 'feeds'라는 이름으로 반환
            // f{.*}는 해당 노드의 모든 속성을 딕셔너리로 변환해 줌
            collect(DISTINCT f { .*, content_type: toString(f.content_type) }) AS feeds,
            
            // 중복을 제거하여 관련 기관 노드들의 리스트를 'organizations'라는 이름으로 반환
            collect(DISTINCT o { .* }) AS organizations
        """
        try:
            # driver를 사용하여 세션을 열고, 해당 세션으로 쿼리를 실행
            async with self.driver.session() as session:
                result = await session.run(cypher_query, keyword=keyword)
                record = await result.single()
            
            if record and record.data().get("keyword"):
                return record.data()
            else:
                # 키워드를 찾지 못한 경우 None을 반환
                return None

        except Exception as e:
            logger.error(f"Error finding nodes for keyword '{keyword}' in Neo4j: {e}", exc_info=True)
            # 서비스 레이어에서 처리할 수 있도록 예외를 다시 발생시킴
            raise