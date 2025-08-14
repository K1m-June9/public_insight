"""
PublicInsight 관리자 대시보드 스키마
관리자 대시보드에서 사용되는 통계 및 현황 데이터 스키마 정의
"""

from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import (
    BaseSchema, 
    BaseResponse, 
    DataResponse,
    StatItem,
    CountInfo
)

# ============================================================================
# 1. 활동 관련 열거형
# ============================================================================

class ActivityType(str, Enum):
    """사용자 활동 유형"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FEED_VIEW = "FEED_VIEW"
    FEED_BOOKMARK = "FEED_BOOKMARK"
    FEED_RATING = "FEED_RATING"
    SEARCH = "SEARCH"
    PROFILE_UPDATE = "PROFILE_UPDATE"

# ============================================================================
# 2. 기본 통계 스키마
# ============================================================================

class DailySignupStat(BaseSchema):
    """일별 가입자 통계"""
    date: date
    count: int

class PopularKeyword(BaseSchema):
    """인기 검색 키워드"""
    keyword: str
    count: int

class OrganizationStat(BaseSchema):
    """기관별 통계"""
    organization_name: str
    feed_count: int

# ============================================================================
# 3. 슬라이더 및 공지사항 통계 스키마
# ============================================================================

class SliderStats(BaseSchema):
    """슬라이더 통계"""
    active: int
    inactive: int

class NoticeStats(BaseSchema):
    """공지사항 통계"""
    active: int
    inactive: int
    pinned: int

# ============================================================================
# 4. 인기 피드 관련 스키마
# ============================================================================

class TopBookmarkedFeed(BaseSchema):
    """북마크 수 기준 인기 피드"""
    id: int
    title: str
    bookmark_count: int
    organization_name: str

class TopRatedFeed(BaseSchema):
    """평점 기준 인기 피드"""
    id: int
    title: str
    average_rating: float
    rating_count: int
    organization_name: str

# ============================================================================
# 5. 사용자 활동 관련 스키마
# ============================================================================

class RecentActivity(BaseSchema):
    """최근 사용자 활동"""
    id: int
    activity_type: ActivityType
    user_name: str
    target_id: Optional[int]
    created_at: datetime

# ============================================================================
# 6. 대시보드 메인 데이터 스키마
# ============================================================================

class DashboardOverview(BaseSchema):
    """대시보드 개요 통계"""
    total_users: int
    active_users: int
    total_feeds: int
    total_organizations: int
    today_signups: int
    total_views: int

class DashboardData(BaseSchema):
    """대시보드 전체 데이터"""
    # 기본 통계
    total_users: int
    active_users: int
    total_feeds: int
    total_organizations: int
    today_signups: int
    total_views: int
    
    # 시계열 데이터
    monthly_signups: List[DailySignupStat]
    
    # 검색 통계
    popular_keywords: List[PopularKeyword]
    
    # 기관 통계
    organization_stats: List[OrganizationStat]
    
    # 콘텐츠 통계
    slider_stats: SliderStats
    notice_stats: NoticeStats
    
    # 인기 피드
    top_bookmarked_feeds: List[TopBookmarkedFeed]
    top_rated_feeds: List[TopRatedFeed]
    
    # 최근 활동
    recent_activities: List[RecentActivity]

# ============================================================================
# 7. 응답 스키마
# ============================================================================

class DashboardResponse(BaseResponse):
    """대시보드 응답"""
    success: bool = True
    data: DashboardData

# ============================================================================
# 8. 추가 유틸리티 스키마 (먼 미래의 확장용)
# ============================================================================

class DateRangeStats(BaseSchema):
    """기간별 통계 (향후 확장용)"""
    start_date: date #시작 날짜
    end_date: date #종료 날짜
    total_signups: int #기간 내 가입자 수
    total_views: int #기간 내 조회수
    total_searches: int #기간 내 검색 수

class SystemHealth(BaseSchema):
    """시스템 상태 (향후 확장용)"""
    database_status: str #데이터베이스 상태
    search_engine_status: str #검색 엔진 상태
    cache_status: str #캐시 상태
    last_updated: datetime #마지막 업데이트 시간

class QuickStats(BaseSchema):
    """빠른 통계 (향후 확장용)"""
    users_online: int #현재 온라인 사용자 수
    searches_today: int #오늘 검색 수
    bookmarks_today: int #오늘 북마크 수

# ============================================================================
# 9. 검증 함수(Service 레이어에서 검증 시 사용 X)
# ============================================================================

def validate_dashboard_date_range(start_date: date, end_date: date) -> bool:
    """대시보드 날짜 범위 검증"""
    if start_date > end_date:
        raise ValueError("시작 날짜는 종료 날짜보다 이전이어야 합니다")
    
    # 최대 1년 범위 제한
    if (end_date - start_date).days > 365:
        raise ValueError("날짜 범위는 최대 1년까지 가능합니다")
    
    return True

def validate_activity_type(activity_type: str) -> bool:
    """활동 유형 검증"""
    valid_types = [e.value for e in ActivityType]
    if activity_type not in valid_types:
        raise ValueError(f"유효하지 않은 활동 유형입니다: {activity_type}")
    
    return True