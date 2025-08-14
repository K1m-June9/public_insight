from elasticsearch import AsyncElasticsearch
from typing import List, Dict, Any

class DashboardActivityRepository:
    """대시보드 통계 중 Elasticsearch 로그 기반 데이터 조회를 담당"""
    def __init__(self, es: AsyncElasticsearch):
        self.es = es

    async def get_popular_keywords(self) -> List[Dict[str, Any]]:
        """가장 많이 검색된 키워드 상위 5개를 조회합니다."""
        # 기존 UsersActivityRepository의 쿼리와 유사하지만, user.id 필터만 없음
        es_query = {
            "query": {
                # event.category가 "SEARCH"인 로그만 대상으로 함
                "term": {"event.category.keyword": "SEARCH"}
            },
            "size": 0,
            "aggs": {
                "popular_keywords": {
                    # url.query 필드의 값을 기준으로 집계
                    "terms": {"field": "url.query.keyword", "size": 5}
                }
            }
        }
        response = await self.es.search(index="logstash-*", body=es_query)
        buckets = response.get("aggregations", {}).get("popular_keywords", {}).get("buckets", [])
        
        # 'q=검색어' 형태에서 '검색어'만 추출하는 로직 추가
        return [
            {"keyword": bucket.get("key", "").split('=')[-1], "count": bucket.get("doc_count", 0)}
            for bucket in buckets
        ]

    async def get_recent_activities(self) -> List[Dict[str, Any]]:
        """가장 최근의 사용자 활동 로그 10개를 조회합니다."""
        es_query = {
            "size": 10,
            "sort": [{"@timestamp": "desc"}]
        }
        response = await self.es.search(index="logstash-*", body=es_query)
        
        activities = []
        for hit in response["hits"]["hits"]:
            source = hit.get("_source", {})
            user_info = source.get("user", {})
            event_info = source.get("event", {})
            
            activities.append({
                "id": int(hit.get("_id").replace("-", "")[:16], 16), # 임시 ID 생성
                "activity_type": event_info.get("action", "UNKNOWN"),
                "user_name": user_info.get("id", "unknown"),
                "target_id": None, # 로그 스키마에 따라 파싱 로직 필요
                "created_at": source.get("@timestamp")
            })
        return activities