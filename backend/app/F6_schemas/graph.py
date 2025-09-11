# ============================================================================
# PoC를 위한 파일: 테스트 용도
# ============================================================================

from typing import List, Optional
from pydantic import BaseModel

#    기존 스키마 구조와 일관성을 유지하기 위해 base 스키마를 import.
#    그러나 그래프 데이터는 구조가 유연하므로, BaseSchema 대신 BaseModel을 직접 상속하여
#    더 자유로운 형태의 데이터 구조를 정의하는 것도 좋은 방법임.
#    우선은 일관성을 위해 BaseSchema를 사용.
from app.F6_schemas.base import BaseSchema, DataResponse

# ============================================================================
# 1. 그래프 노드를 표현하는 기본 스키마
# ============================================================================

class GraphNode(BaseSchema):
    """그래프에서 반환되는 단일 노드를 표현하는 기본 스키마."""
    id: int
    label: str # 노드의 레이블 (예: "User", "Feed")
    properties: dict # 노드가 가진 속성들 (예: {"title": "..."})

class RelatedUserNode(BaseSchema):
    """관계 분석에 사용될 사용자 노드의 최소 정보."""
    id: int
    user_id: str
    nickname: str

class RelatedFeedNode(BaseSchema):
    """관계 분석에 사용될 피드 노드의 최소 정보."""
    id: int
    title: str

class RelatedOrganizationNode(BaseSchema):
    """관계 분석에 사용될 기관 노드의 최소 정보."""
    id: int
    name: str

class RelatedCategoryNode(BaseSchema):
    """관계 분석에 사용될 카테고리 노드의 최소 정보."""
    id: int
    name: str
    
class RatedRelationship(BaseSchema):
    """RATED 관계의 속성을 담는 스키마."""
    score: int

# ============================================================================
# 2. PoC API 응답 데이터 스키마
# ============================================================================

class FeedRelationsData(BaseSchema):
    """
    특정 피드와 직접적으로 연결된 이웃 노드들의 정보를 담는 스키마.
    PoC API의 실제 데이터 구조임.
    """
    source_feed: RelatedFeedNode
    published_by: Optional[RelatedOrganizationNode] = None
    belongs_to: Optional[RelatedCategoryNode] = None
    bookmarked_by_users: List[RelatedUserNode] = []
    rated_by_users: List[RelatedUserNode] = []
    # (선택적 확장) 각 사용자의 평점 정보를 함께 반환할 수도 있음
    # ratings_with_users: List[Tuple[RelatedUserNode, RatedRelationship]] = []


# ============================================================================
# 3. 최종 API 응답 래퍼(Wrapper) 스키마
# ============================================================================

class FeedRelationsResponse(DataResponse):
    """
    GET /graph/feeds/{id}/related API의 최종 응답 스키마.
    """
    data: FeedRelationsData