from pydantic import BaseModel, Field, ConfigDict  # [수정] ConfigDict 임포트
from typing import Optional, Dict, List
from datetime import datetime, date
from enum import Enum

# 'PaginationInfo'는 base.py에 정의되어 있다고 가정합니다.
# 이 파일에 있는 공통 스키마들은 실제로는 base.py에 위치하는 것이 좋습니다.
from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationInfo 

# 
# ============================================================================
# 공통 스키마 (실제로는 app/F6_schemas/base.py 파일에 위치해야 함)
# ============================================================================

class BaseSchema(BaseModel):
    """공통 베이스 스키마"""
    # [수정] Pydantic 2.x 버전에 맞게 ConfigDict 사용
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True
    )

class BaseResponse(BaseModel):
    """기본 응답 구조"""
    success: bool

class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    code: str
    message: str
    details: Optional[Dict[str, str]] = None

class ErrorResponse(BaseResponse):
    """에러 응답"""
    error: ErrorDetail

# ============================================================================
# 7. 정렬 옵션 열거형 (SearchQuery에서 사용하므로 위로 이동)
# ============================================================================

class SortOption(str, Enum):
    """정렬 옵션"""
    RELEVANCE = "relevance"
    LATEST = "latest"
    OLDEST = "oldest"
    VIEWS = "views"
    RATING = "rating"

# ============================================================================
# 1. 검색 쿼리 파라미터 스키마
# ============================================================================

class SearchQuery(BaseModel):
    """검색 쿼리 파라미터"""
    q: Optional[str] = Field(default=None, max_length=100, description="검색 키워드")
    organizations: Optional[str] = Field(default=None, description="기관 필터 (쉼표 구분)")
    categories: Optional[str] = Field(default=None, description="카테고리 필터 (쉼표 구분)")
    types: Optional[str] = Field(default=None, description="콘텐츠 유형 필터 (쉼표 구분)")
    date_from: Optional[date] = Field(default=None, description="시작 날짜 (YYYY-MM-DD)")
    date_to: Optional[date] = Field(default=None, description="종료 날짜 (YYYY-MM-DD)")
    
    # [수정] regex -> pattern으로 변경하고, 더 나은 방법인 Enum을 사용
    sort: SortOption = Field(default=SortOption.RELEVANCE, description="정렬 방식")
    
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 결과 수")

# ============================================================================
# 2. 검색 결과 관련 스키마
# ============================================================================

class SearchOrganization(BaseSchema):
    """검색 결과 기관 정보"""
    id: int
    name: str
    logo_url: str

class SearchCategory(BaseSchema):
    """검색 결과 카테고리 정보"""
    id: int
    name: str

class SearchHighlight(BaseSchema):
    """검색 하이라이트"""
    title: str
    summary: str

class SearchResultItem(BaseSchema):
    """검색 결과 항목"""
    id: int
    title: str
    summary: str
    organization: SearchOrganization
    category: SearchCategory
    type: str
    published_date: datetime
    view_count: int
    average_rating: float
    bookmark_count: int
    url: str
    highlight: SearchHighlight

# ============================================================================
# 3. 검색 필터 및 쿼리 정보 스키마
# ============================================================================

class SearchDateRange(BaseModel):
    """검색 날짜 범위"""
    # [수정] alias가 필요한 경우 from_attributes=True와 함께 사용하기 위해 model_config 추가
    model_config = ConfigDict(from_attributes=True)
    from_date: Optional[date] = Field(alias="from", default=None)
    to_date: Optional[date] = Field(alias="to", default=None)

class SearchFilters(BaseModel):
    """검색 필터 정보"""
    organizations: List[str]
    categories: List[str]
    types: List[str]
    date_range: SearchDateRange

class SearchQueryInfo(BaseModel):
    """검색 쿼리 정보"""
    keyword: Optional[str]
    filters: SearchFilters
    sort: str

# ============================================================================
# 4. 페이지네이션 스키마
# ============================================================================

class SearchPagination(BaseModel):
    """검색 페이지네이션"""
    current_page: int
    total_pages: int
    total_count: int
    limit: int
    has_next: bool
    has_previous: bool

# ============================================================================
# 5. 집계 데이터 스키마
# ============================================================================

class AggregationItem(BaseModel):
    """집계 항목"""
    name: str
    count: int

class SearchAggregations(BaseModel):
    """검색 집계 데이터"""
    organizations: List[AggregationItem]
    categories: List[AggregationItem]
    types: List[AggregationItem]
    date_ranges: List[AggregationItem]

# ============================================================================
# 6. 검색 응답 스키마
# ============================================================================

class SearchData(BaseModel):
    """검색 응답 데이터"""
    query: SearchQueryInfo
    results: List[SearchResultItem]
    pagination: SearchPagination
    aggregations: SearchAggregations
    search_time: str

class SearchResponse(BaseResponse):
    """검색 응답"""
    data: SearchData

# ============================================================================
# 8. 콘텐츠 유형 열거형 (참고용으로 유지)
# ============================================================================

class ContentType(str, Enum):
    """콘텐츠 유형"""
    POLICY = "정책"
    PRESS_RELEASE = "보도자료"
    ANNOUNCEMENT = "공고"
    REPORT = "보고서"