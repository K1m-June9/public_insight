from elasticsearch import AsyncElasticsearch 
from typing import List, Dict, Any, Tuple

# 사용자 활동 관련 데이터를 Elasticsearch에서 조회하는 역할을 담당하는 클래스
class UsersActivityRepository:
    """
    Elasticsearch에 저장된 사용자 활동 로그를 조회하고 통계를 계산하는 저장소(Repository)
    데이터베이스(Elasticsearch)와의 직접적인 통신을 담당
    """
    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    # 특정 사용자의 Elasticsearch 기반 통계를 비동기적으로 조회하는 메소드
    async def get_es_user_statistics(self, user_id: str) -> dict:
        """
        Elasticsearch에서 특정 사용자의 총 검색 횟수와 마지막 활동 시간을 조회
        - param user_id: 통계를 조회할 사용자의 고유 ID
        - return: total_searches와 last_activity_at 을 포함하는 딕셔너리
        """
        es_query = {
            # 1. [조회대상 지정]: 어떤 문서들을 대상으로 할지 정의하는 부분
            # 'term' 쿼리: 특정 필드에서 정확히 일치하는 값을 가진 문서를 찾음
            # user.user_id 필드가 입력받은 user_id와 일치하는 모든 로그를 대상으로 함
            "query": {
                "term": {"user.id.keyword": user_id},
            },

            # 2. [결과 크기 설정]: 검색 결과를 몇 개나 가져올지 설정
            # 'size'를 0으로 설정하여 실제 검색된 문서는 반환하지 않도록 함(성능 최적화)
            # 문서 내용이 아니라 오직 통계 결과(aggs)에만 관심있기 때문
            "size": 0,

            # 3. [집계(Aggregations)설정]: 조회 대상 문서들로 어떤 통계를 계산할지 정의
            "aggs": {
                # 'total_searches'라는 이름으로 집계 결과를 생성
                # 'filter' 집계: 특정 조건을 만족하는 문서들만으로 하위 집계를 수행
                "total_searches": {"filter": {"term": {"event.category.keyword": "SEARCH"}}},

                # 'last_activity_at'이라는 이름으로 집계 결과를 생성
                # 'max' 집계: 특정 필드의 최댓값을 계산
                # '@timestamp' 필드(로그 기록 시간)의 최댓값을 찾아 사용자의 마지막 활동 시간을 알아냄
                "last_activity_at": {"max": {"field": "@timestamp"}}
            }
        }


        # 정의한 쿼리를 사용하여 Elasticsearch의 search API를 비동기적으로 호출
        # 'index'는 검색할 대상 인덱스 패턴을 지정(logstash-로 시작하는 모든 인덱스)
        # 'body'에는 위에서 정의한 쿼리 딕셔너리 전달
        response = await self.es.search(index="logstash-*", body=es_query)

        # Elasticsearch 응답에서 'aggregations' 키에 해당하는 값을 가져옴
        # 없을 경우 빈 딕셔너리를 반환
        aggs = response.get("aggregations", {})

        # 최종적으로 계산된 통계 데이터를 딕셔너리 형태로 반환
        return {
            "total_searches": aggs.get("total_searches", {}).get("doc_count", 0),
            "last_activity_at": aggs.get("last_activity_at", {}).get("value_as_string")
        }

    async def get_paginated_activity_logs(self, user_id: str, page:int, limit: int) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Elasticsearch에서 특정 사용자의 활동 로그를 페이지네이션하여 조회
        : return (로그 수, 로그 목록) 튜플
        """

        # 페이지네이션을 위한 계산
        from_offset = (page - 1) * limit 

        es_query = {
            "query": {
                "term": {
                    "user.id.keyword": user_id
                }
            },
            "sort": [
                {"@timestamp": "desc"} # 최신 로그부터 정렬
            ],
            "from": from_offset, # 시작 위치
            "size": limit # 가져올 개수
        }

        response = await self.es.search(index="logstash-*", body=es_query)

        # 전체 적중 개수
        total_count = response["hits"]["total"]["value"]

        # 실제 로그 데이터 추출 및 가공
        activities = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"] # 로그의 원본 JSON 데이터
            # 응답 스키마에 맞게 데이터 가공
            activities.append({
                "id": hit["_id"], # ES 문서의 고유 ID를 사용
                "activity_type": source.get("event", {}).get("category", ["UNKNOWN"])[0], # 예: "BOOKMARK"
                "target_id": source.get("url", {}).get("path", "").split('/')[-1] if "detail" in source.get("url", {}).get("path", "") else None,
                "ip_address": source.get("client", {}).get("ip"),
                "user_agent": source.get("http", {}).get("request", {}).get("user_agent"),
                "created_at": source.get("@timestamp")
            })
        
        return total_count, activities