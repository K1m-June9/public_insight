from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationInfo

# ============================================================================
# 공통 피드 관련 스키마
# ============================================================================

class OrganizationInfo(BaseSchema):
    """기관 기본 정보"""
    id: int
    name: str

class CategoryInfo(BaseSchema):
    """카테고리 기본 정보"""
    id: int
    name: str

# ============================================================================
# 1. 메인 페이지 피드 목록 관련 스키마
# ============================================================================

class MainFeedItem(BaseSchema):
    """메인 페이지 피드 항목"""
    id: int
    title: str
    organization: OrganizationInfo
    summary: str
    published_date: datetime
    view_count: int
    average_rating: float

class MainFeedListData(BaseModel):
    """메인 페이지 피드 목록 데이터"""
    feeds: List[MainFeedItem]
    pagination: PaginationInfo

class MainFeedListResponse(BaseResponse):
    """메인 페이지 피드 목록 응답"""
    data: MainFeedListData

class FeedListQuery(BaseModel):
    """피드 목록 쿼리 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수 (최대 100)")

# ============================================================================
# 2. 기관 페이지 피드 목록 관련 스키마
# ============================================================================

class OrganizationFeedItem(BaseSchema):
    """기관 페이지 피드 항목"""
    id: int
    title: str
    category: CategoryInfo
    summary: str
    published_date: datetime
    view_count: int
    average_rating: float

class FeedFilter(BaseModel):
    """피드 필터 정보"""
    category_id: int
    category_name: str

class OrganizationFeedListData(BaseModel):
    """기관 페이지 피드 목록 데이터"""
    organization: OrganizationInfo
    feeds: List[OrganizationFeedItem]
    pagination: PaginationInfo
    filter: Optional[FeedFilter] = None

class OrganizationFeedListResponse(BaseResponse):
    """기관 페이지 피드 목록 응답"""
    data: OrganizationFeedListData

class OrganizationFeedQuery(BaseModel):
    """기관 피드 쿼리 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수 (최대 100)")
    category_id: Optional[int] = Field(default=None, description="카테고리 ID (선택사항)")

# ============================================================================
# 3. 최신 피드 슬라이드 관련 스키마
# ============================================================================

class LatestFeedItem(BaseSchema):
    """최신 피드 항목 (메인페이지용)"""
    id: int
    title: str
    organization: OrganizationInfo

class LatestFeedData(BaseModel):
    """최신 피드 데이터 (메인페이지용)"""
    feeds: List[LatestFeedItem]
    count: int

class LatestFeedResponse(BaseResponse):
    """최신 피드 응답 (메인페이지용)"""
    data: LatestFeedData

class OrganizationLatestFeedItem(BaseSchema):
    """최신 피드 항목 (기관페이지용)"""
    id: int
    title: str
    category: CategoryInfo

class OrganizationLatestFeedData(BaseModel):
    """최신 피드 데이터 (기관페이지용)"""
    organization: OrganizationInfo
    feeds: List[OrganizationLatestFeedItem]
    count: int

class OrganizationLatestFeedResponse(BaseResponse):
    """최신 피드 응답 (기관페이지용)"""
    data: OrganizationLatestFeedData

class LatestFeedQuery(BaseModel):
    """최신 피드 쿼리 파라미터"""
    limit: int = Field(default=10, ge=1, le=50, description="최대 항목 수")

# ============================================================================
# 4. TOP5 피드 관련 스키마
# ============================================================================

class Top5FeedItem(BaseSchema):
    """TOP5 피드 항목"""
    id: int
    title: str
    average_rating: float
    view_count: int
    bookmark_count: int
    organization: str

class Top5FeedData(BaseModel):
    """TOP5 피드 데이터"""
    top_rated: List[Top5FeedItem]
    most_viewed: List[Top5FeedItem]
    most_bookmarked: List[Top5FeedItem]

class Top5FeedResponse(BaseResponse):
    """TOP5 피드 응답"""
    data: Top5FeedData

class Top5FeedQuery(BaseModel):
    """TOP5 피드 쿼리 파라미터"""
    limit: int = Field(default=5, ge=1, le=10, description="각 카테고리별 피드 수")

# ============================================================================
# 5. 보도자료 관련 스키마
# ============================================================================

class PressReleaseItem(BaseSchema):
    """보도자료 항목"""
    id: int
    title: str
    category: CategoryInfo
    summary: str
    published_date: datetime
    view_count: int
    average_rating: float

class PressReleaseData(BaseModel):
    """보도자료 데이터"""
    organization: OrganizationInfo
    press_releases: List[PressReleaseItem]
    pagination: PaginationInfo

class PressReleaseResponse(BaseResponse):
    """보도자료 응답"""
    data: PressReleaseData

class PressReleaseQuery(BaseModel):
    """보도자료 쿼리 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)")
    limit: int = Field(default=15, ge=1, le=100, description="페이지당 항목 수 (최대 100)")

# ============================================================================
# 6. 피드 상세 관련 스키마 (PDF 버전)
# ============================================================================

class FeedDetail(BaseSchema):
    """피드 상세 정보"""
    id: int
    title: str
    organization: OrganizationInfo
    category: CategoryInfo
    average_rating: float
    view_count: int
    published_date: datetime
    # content: str  삭제(히스토리 보려고 만듦)
    source_url: str

    # PDF 파일에 직접 접근할 수 있는 URL
    pdf_url: str
    
    # 로그인한 사용자에게만 제공될 선택적 정보(선택적 인증)
    is_bookmarked: Optional[bool] = None
    user_rating: Optional[int] = None

class FeedDetailData(BaseModel):
    """피드 상세 데이터"""
    feed: FeedDetail

class FeedDetailResponse(BaseResponse):
    """피드 상세 응답"""
    data: FeedDetailData

# ============================================================================
# 7. 북마크 관련 스키마
# ============================================================================

class BookmarkRequest(BaseModel):
    """북마크 요청 (빈 객체)"""
    pass

class BookmarkData(BaseModel):
    """북마크 응답 데이터"""
    is_bookmarked: bool
    bookmark_count: int
    message: str

class BookmarkResponse(BaseResponse):
    """북마크 응답"""
    data: BookmarkData

# ============================================================================
# 8. 별점 관련 스키마
# ============================================================================

class RatingRequest(BaseModel):
    """별점 요청"""
    score: int = Field(..., ge=1, le=5, description="별점 (1-5점)")

class RatingData(BaseModel):
    """별점 응답 데이터"""
    user_rating: int
    average_rating: float
    total_ratings: int
    message: str

class RatingResponse(BaseResponse):
    """별점 응답"""
    data: RatingData

# ============================================================================
# 9. 경로 파라미터 스키마
# ============================================================================

class FeedPathParams(BaseModel):
    """피드 경로 파라미터"""
    id: int = Field(..., gt=0, description="피드 ID (양의 정수)")

class OrganizationPathParams(BaseModel):
    """기관명 경로 파라미터"""
    organization_name: str = Field(..., min_length=1, description="기관명")
