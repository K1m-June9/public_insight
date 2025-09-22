import logging
from typing import Dict, Any, List

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

    async def expand_from_feed(self, feed_id: int) -> List[Dict[str, Any]] | None:
        """피드 노드에서 확장을 시작함. (Neo4j 4.4 호환 쿼리로 수정)"""
        # 🔧 [수정] 각 CALL의 결과를 WITH로 받아, 최종적으로 RETURN 하도록 구조 변경
        cypher_query = """
        MATCH (start_feed:Feed {id: $feed_id})
        CALL {
            WITH start_feed
            MATCH (start_feed)-[r:IS_SIMILAR_TO]-(similar_feed:Feed)
            RETURN similar_feed AS node, 'similar_feed' AS type, r.score AS meta
            ORDER BY r.score DESC LIMIT 2
        }
        WITH start_feed, collect({node: node, type: type, meta: meta}) AS results1
        
        CALL {
            WITH start_feed
            MATCH (start_feed)<-[:BOOKMARKED]-(u:User)-[b:BOOKMARKED]->(rec_feed:Feed)
            WHERE start_feed <> rec_feed
            RETURN rec_feed AS node, 'recommended_feed' AS type, count(u) AS meta
            ORDER BY count(u) DESC LIMIT 2
        }
        WITH results1 + collect({node: node, type: type, meta: meta}) AS results2, start_feed

        CALL {
            WITH start_feed
            MATCH (start_feed)-[r:CONTAINS_KEYWORD]->(keyword:Keyword)
            RETURN keyword AS node, 'related_keyword' AS type, r.score AS meta
            ORDER BY r.score DESC LIMIT 2
        }
        WITH results2 + collect({node: node, type: type, meta: meta}) AS final_results
        
        UNWIND final_results AS result
        RETURN result.node AS node, result.type AS type, result.meta AS meta
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query, feed_id=feed_id)
            return [record.data() async for record in result]

    async def expand_from_organization(self, org_id: int) -> List[Dict[str, Any]] | None:
        """기관 노드에서 확장을 시작함. (Neo4j 4.4 호환 쿼리로 수정)"""
        # 🔧 [수정] 쿼리 구조 변경
        cypher_query = """
        MATCH (start_org:Organization {id: $org_id})
        CALL {
            WITH start_org
            MATCH (start_org)-[:PUBLISHED]->(feed:Feed)
            OPTIONAL MATCH (feed)<-[r:RATED]-(u:User)
            OPTIONAL MATCH (feed)<-[b:BOOKMARKED]-(u2:User)
            WITH feed, avg(r.score) AS avg_rating, count(DISTINCT b) AS bookmark_count
            WITH feed, (coalesce(avg_rating, 0) * 10) + bookmark_count AS popularity_score
            RETURN feed AS node, 'popular_feed' AS type, popularity_score AS meta
            ORDER BY popularity_score DESC LIMIT 2
        }
        WITH start_org, collect({node: node, type: type, meta: meta}) AS results1

        CALL {
            WITH start_org
            MATCH (start_org)-[:PUBLISHED]->(f:Feed)-[r:CONTAINS_KEYWORD]->(keyword:Keyword)
            RETURN keyword AS node, 'major_keyword' AS type, sum(r.score) AS meta
            ORDER BY sum(r.score) DESC LIMIT 3
        }
        WITH results1 + collect({node: node, type: type, meta: meta}) AS final_results

        UNWIND final_results AS result
        RETURN result.node AS node, result.type AS type, result.meta AS meta
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query, org_id=org_id)
            return [record.data() async for record in result]

    async def expand_from_keyword(self, keyword: str) -> List[Dict[str, Any]] | None:
        """키워드 노드에서 확장을 시작함. (Neo4j 4.4 호환 쿼리로 수정)"""
        # 🔧 [수정] 쿼리 구조 변경
        cypher_query = """
        MATCH (start_key:Keyword {name: $keyword})
        CALL {
            WITH start_key
            MATCH (start_key)<-[r:CONTAINS_KEYWORD]-(feed:Feed)
            OPTIONAL MATCH (feed)<-[rate:RATED]-(u:User)
            OPTIONAL MATCH (feed)<-[b:BOOKMARKED]-(u2:User)
            WITH feed, avg(rate.score) AS avg_rating, count(DISTINCT b) AS bookmark_count
            WITH feed, (coalesce(avg_rating, 0) * 10) + bookmark_count AS popularity_score
            RETURN feed AS node, 'popular_feed' AS type, popularity_score AS meta
            ORDER BY popularity_score DESC LIMIT 2
        }
        WITH start_key, collect({node: node, type: type, meta: meta}) AS results1

        CALL {
            WITH start_key
            MATCH (start_key)<-[:SEARCHED]-(u:User)-[:SEARCHED]->(other_key:Keyword)
            WHERE start_key <> other_key
            RETURN other_key AS node, 'related_keyword_by_search' AS type, count(u) AS meta
            ORDER BY count(u) DESC LIMIT 2
        }
        WITH results1 + collect({node: node, type: type, meta: meta}) AS final_results
        
        UNWIND final_results AS result
        RETURN result.node AS node, result.type AS type, result.meta AS meta
        """
        async with self.driver.session() as session:
            result = await session.run(cypher_query, keyword=keyword)
            return [record.data() async for record in result]

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