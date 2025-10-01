from datetime import datetime
from typing import List, Optional

from app.F6_schemas.base import BaseSchema, DataResponse

# ============================================================================
# 1. 추천 결과 항목 스키마
# ============================================================================

class RecommendedFeedItem(BaseSchema):
    """
    추천된 단일 피드 항목의 정보를 담는 스키마
    """
    id: int
    title: str
    summary: Optional[str] = None # NLP 요약문이 있다면 포함
    
    # 소속 기관 및 카테고리 정보
    organization_name: str
    category_name: str
    
    # 콘텐츠의 원본 발행 일시
    published_date: Optional[datetime] = None

    # (선택적) 디버깅이나 프론트엔드에서 활용할 수 있도록 유사도 점수를 포함
    similarity_score: Optional[float] = None
    
    class Config:
        # 이 옵션은 SQLAlchemy 모델의 관계(relationship)를 통해
        # organization.name과 같은 속성에 접근할 수 있게 해줌
        # 하지만 우리는 서비스 레이어에서 수동으로 매핑할 것이므로 필수는 아님
        from_attributes = True

# ============================================================================
# 2. 추천 API 응답 데이터 스키마
# ============================================================================

class RecommendationResultData(BaseSchema):
    """
    추천 API의 최종 응답 데이터 구조
    '정책 자료'와 '보도자료' 추천 목록을 각각 담가버림
    """
    # 현재 피드가 '정책 자료'일 경우, 이 필드는 '함께 보기 좋은 정책 자료' 목록이 됨
    # 현재 피드가 '보도자료'일 경우, 이 필드는 '관련 정책 자료' 목록이 됨
    main_recommendations: List[RecommendedFeedItem]

    # 현재 피드가 '정책 자료'일 경우, 이 필드는 '관련 보도자료' 목록이 됨
    # 현재 피드가 '보도자료'일 경우, 이 필드는 '함께 보기 좋은 보도자료' 목록이 됨
    sub_recommendations: List[RecommendedFeedItem]

# ============================================================================
# 3. 최종 API 응답 래퍼(Wrapper) 스키마
# ============================================================================

class RecommendationResponse(DataResponse):
    """
    GET /feeds/{feed_id}/recommendations API의 최종 응답 스키마.
    기존의 DataResponse를 상속받아 일관성을 유지합니다.
    """
    data: RecommendationResultData