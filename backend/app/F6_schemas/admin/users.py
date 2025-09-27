from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse, PaginatedResponse, PaginationQuery, PaginationInfo

# =======================
# 1. 사용자 관련 열거형
# =======================

class UserRole(str, Enum):
    """사용자 역할"""
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class UserStatus(str, Enum):
    """사용자 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class ActivityType(str, Enum):
    """활동 유형"""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    FEED_VIEW = "FEED_VIEW"
    FEED_BOOKMARK = "FEED_BOOKMARK"
    FEED_RATING = "FEED_RATING"
    SEARCH = "SEARCH"
    PROFILE_UPDATE = "PROFILE_UPDATE"


# =======================
# 2. 사용자 스키마
# =======================
class UserListItem(BaseSchema):
    """사용자 목록 항목"""
    id: int
    user_id: str
    nickname: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime

class UserDetail(BaseSchema):
    """사용자 상세 정보"""
    id: int
    user_id: str
    email: str
    nickname: str
    role: UserRole
    status: UserStatus
    terms_agreed: bool
    privacy_agreed: bool
    notification_agreed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    statistics: "UserStatistics"

class UserStatistics(BaseSchema):
    """사용자 통계"""
    total_bookmarks: int
    total_ratings: int
    total_searches: int
    total_activities: int
    last_activity_at: Optional[datetime]


class UserActivity(BaseSchema):
    """사용자 활동 로그"""
    id: int
    activity_type: ActivityType
    target_id: Optional[int]
    ip_address: str
    user_agent: str
    created_at: datetime

class UserRoleStats(BaseSchema):
    """역할별 사용자 통계"""
    admin: int
    moderator: int
    user: int

class UserStatusStats(BaseSchema):
    """상태별 사용자 통계"""
    active: int
    inactive: int
    suspended: int
    deleted: int

class UserListStatistics(BaseSchema):
    """사용자 목록 통계"""
    total_users: int
    by_role: UserRoleStats
    by_status: UserStatusStats

class UserRoleUpdate(BaseSchema):
    """사용자 권한 변경 결과"""
    id: int
    user_id: str
    nickname: str
    role: UserRole
    updated_at: datetime

class UserStatusUpdate(BaseSchema):
    """사용자 상태 변경 결과"""
    id: int
    user_id: str
    nickname: str
    status: UserStatus
    updated_at: datetime

# =======================
# 3. 요청 스키마
# =======================

class UserListRequest(PaginationQuery):
    """사용자 목록 조회 요청"""
    search: Optional[str] = Field(None, description="검색어")
    role: Optional[UserRole] = Field(None, description="역할 필터")
    status: Optional[UserStatus] = Field(None, description="상태 필터")

# 유저 증가 시 limit default(50)으로 따로 작성 예정(현재 20, base)
class UserActivityRequest(PaginationQuery):
    """사용자 활동 로그 조회 요청"""
    pass

class UserRoleChangeRequest(BaseModel):
    """사용자 권한 변경 요청"""
    role: UserRole = Field(..., description="변경할 역할")

class UserStatusChangeRequest(BaseModel):
    """사용자 상태 변경 요청"""
    status: UserStatus = Field(..., description="변경할 상태")

# =======================
# 4. 응답 스키마
# =======================

class UserListData(BaseSchema):
    """사용자 목록 데이터"""
    users: List[UserListItem]
    pagination: PaginationInfo
    statistics: UserListStatistics

class UserListResponse(BaseResponse):
    """사용자 목록 응답"""
    success: bool = True
    data: UserListData

class UserDetailResponse(BaseResponse):
    """사용자 상세 응답"""
    success: bool = True
    data: UserDetail

class UserActivityData(BaseSchema):
    """사용자 활동 로그 데이터"""
    activities: List[UserActivity]
    pagination: PaginationInfo

class UserActivityResponse(BaseResponse):
    """사용자 활동 로그 응답"""
    success: bool = True
    data: UserActivityData

class UserRoleChangeResponse(BaseResponse):
    """사용자 권한 변경 응답"""
    success: bool = True
    data: UserRoleUpdate

class UserStatusChangeResponse(BaseResponse):
    """사용자 상태 변경 응답"""
    success: bool = True
    data: UserStatusUpdate

# =======================
# 5. 경로 파라미터 스키마
# =======================

class UserPathParams(BaseModel):
    """사용자 경로 파라미터"""
    id: int = Field(..., ge=1, description="사용자 ID")

# =======================
# 6. 설정 및 상수(안써도됨, 일단 만든거)
# =======================

class UserManagement:
    """사용자 관리"""
    # 검색 설정
    SEARCH_FIELDS = ["user_id", "nickname", "email"]

    # 권한 변경 규칙
    ROLE_CHANGE_RULES = {
        UserRole.ADMIN: [],  # ADMIN 권한은 변경 불가
        UserRole.MODERATOR: [UserRole.USER],  # MODERATOR는 USER로만 변경 가능
        UserRole.USER: [UserRole.MODERATOR]  # USER는 MODERATOR로만 승격 가능
    }

    # 상태 변경 (모든 상태 간 변경 가능)
    ALLOWED_STATUS_CHANGES = list(UserStatus)

    # 정렬 우선순위
    ROLE_PRIORITY = {
        UserRole.ADMIN: 1,
        UserRole.MODERATOR: 2,
        UserRole.USER: 3
    }

# =======================
# 7. 유틸리티 함수(Service 레이어에서 검증 시 사용 X)
# =======================

# def can_change_role(current_role: UserRole, target_role: UserRole) -> bool:
#     """권한 변경 가능 여부 확인"""
#     if current_role == UserRole.ADMIN:
#         return False  # ADMIN 권한은 변경 불가

#     allowed_roles = UserManagementSettings.ROLE_CHANGE_RULES.get(current_role, [])
#     return target_role in allowed_roles

# def get_role_priority(role: UserRole) -> int:
#     """역할 우선순위 반환"""
#     return UserManagementSettings.ROLE_PRIORITY.get(role, 999)
