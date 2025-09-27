from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal

# 우리 프로젝트의 기본 응답 구조를 임포트
from app.F6_schemas.base import BaseResponse, ErrorDetail

# ====================================================================
# API 1: GET /api/v1/graph/explore
# 키워드 중심의 초기 마인드맵 데이터를 위한 스키마
# ====================================================================

class GraphNode(BaseModel):
    """마인드맵의 개별 노드를 나타내는 스키마 (기존 NodeData와 동일)."""
    id: str = Field(..., description="노드의 고유 식별자")
    type: Literal['keyword', 'feed', 'organization', 'user', 'anonymous_user'] = Field(..., description="노드의 종류")
    label: str = Field(..., description="노드에 표시될 이름")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")


class GraphEdge(BaseModel):
    """마인드맵의 엣지(관계)를 나타내는 스키마 (기존 EdgeData와 동일)."""
    id: str = Field(..., description="엣지의 고유 식별자")
    source: str = Field(..., description="시작 노드 ID")
    target: str = Field(..., description="타겟 노드 ID")
    label: str | None = Field(None, description="엣지에 표시될 이름")


class ExploreGraphData(BaseModel):
    """GET /explore API의 성공 응답의 'data' 필드에 들어갈 내용."""
    # 🔧 [패턴 적용] XxxData 스키마 정의
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class ExploreGraphResponse(BaseResponse):
    """GET /explore API의 최종 응답 스키마."""
    # 🔧 [패턴 적용] XxxResponse 스키마 정의. BaseResponse 상속.
    data: ExploreGraphData | None = None
# ====================================================================
# 쿼리 파라미터를 위한 스키마
# ====================================================================
class ExploreQuery(BaseModel):
    """GET /explore API의 쿼리 파라미터를 위한 스키마."""
    keyword: str = Field(..., description="탐색의 중심이 될 키워드")


class ExpandQuery(BaseModel):
    """GET /expand API의 쿼리 파라미터를 위한 스키마."""
    node_id: str = Field(..., description="확장할 노드의 고유 ID")
    node_type: str = Field(..., description="확장할 노드의 타입")


# ====================================================================
# API 2: GET /api/v1/graph/wordcloud를 위한 스키마 (메인 페이지, 기관 페이지 같이씀)
# 결국 열심히 만들고 바꾸고 다시 바꾸고 다시 수정하고 변경한 기존 API와 테이블은 사용하지 않을듯
# 갑자기 좉나 슬퍼지네
# ====================================================================
class WordCloudItem(BaseModel):
    text: str = Field(..., description="키워드 텍스트")
    value: float = Field(..., description="키워드의 가중치 또는 빈도수")

class WordCloudResponse(BaseResponse):
    data: List[WordCloudItem] | None = None

# ====================================================================
# API 3: GET /api/v1/graph/feeds/{feed_id}/related-keywords
# 피드 상세 페이지의 '관련 키워드' 섹션을 위한 스키마
# ====================================================================

class RelatedKeywordItem(BaseModel):
    """
    피드와 연관된 개별 키워드 항목을 나타내는 스키마.
    - WordCloudItem과 유사하지만, 명확한 역할 구분을 위해 별도로 정의함.
    """
    text: str = Field(..., description="키워드 텍스트")
    
    # [핵심] 'value' 대신 'score'라는 명확한 필드명을 사용하고,
    # 0에서 100 사이의 정수 값만 허용하도록 유효성 검사를 추가함.
    score: int = Field(..., ge=0, le=100, description="연관도 점수 (0-100)")


class RelatedKeywordsResponse(BaseResponse):
    """
    GET /feeds/{feed_id}/related-keywords API의 최종 응답 스키마.
    """
    # 성공 시에는 RelatedKeywordItem의 리스트를, 실패 시에는 None을 반환.
    data: List[RelatedKeywordItem] | None = None