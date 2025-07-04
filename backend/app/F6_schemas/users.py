from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationInfo

# =================================
# 1. 북마크 관련 스키마
# =================================

# class BookmarkItem(BaseSchema):
#     """북마크 항목 정보"""
#     feed_id: int
#     feed_title: str
#     organization_id: int
#     organization_name: str
#     category_id: int
#     category_name: str
#     view_count: int
#     published_date: datetime
#     bookmarked_at: datetime

# class UserBookmarkListData(BaseModel):
#     """북마크 목록 데이터"""
#     bookmarks: List[BookmarkItem]
#     pagination: PaginationInfo

# class UserBookmarkListResponse(BaseResponse):
#     """북마크 목록 응답"""
#     data: UserBookmarkListData

# class UserBookmarkListQuery(BaseModel):
#     """북마크 목록 쿼리 파라미터"""
#     page: int = 1
#     limit: int = Field(default=20, le=20)


# =================================
# 2. 별점 관련 스키마
# =================================

class RatingItem(BaseSchema):
    """별점 항목 정보"""
    feed_id: int
    feed_title: str
    organization_id: int
    organization_name: str
    category_id: int
    category_name: str
    view_count: int
    published_date: datetime
    user_rating: int
    average_rating: float
    rated_at: datetime

class UserRatingListData(BaseModel):
    """별점 목록 데이터"""
    ratings: List[RatingItem]
    pagination: PaginationInfo

class UserRatingListResponse(BaseResponse):
    """별점 목록 응답"""
    data: UserRatingListData

class UserRatingListQuery(BaseModel):
    """별점 목록 쿼리 파라미터"""
    page: int = 1
    limit: int = Field(default=20, le=20)

# =================================
# 3. 프로필 관련 스키마
# =================================

class UserProfile(BaseSchema):
    """사용자 프로필 정보"""
    user_id: str
    nickname: str
    email: str
    updated_at: Optional[datetime] = None

class UserProfileData(BaseModel):
    """프로필 조회 데이터"""
    user: UserProfile

class UserProfileResponse(BaseResponse):
    """프로필 조회 응답"""
    data: UserProfileData

class UserProfileUpdateRequest(BaseModel):
    """프로필 수정 요청"""
    nickname: str = Field(..., min_length=2, max_length=50)

class UserNickNameUpdateRequest(BaseModel):
    """닉네임 수정 요청"""
    nickname: str = Field(..., min_length=2, max_length=50)

class UserProfileUpdateData(BaseModel):
    """프로필 수정 응답 데이터"""
    user: UserProfile

class UserProfileUpdateResponse(BaseResponse):
    """프로필 수정 응답"""
    message: str
    data: UserProfileUpdateData

# =================================
# 4. 비밀번호 관련 스키마
# =================================

class UserPasswordUpdateRequest(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class UserPasswordUpdateResponse(BaseResponse):
    """비밀번호 변경 응답"""
    message: str

# =================================
# 5. 관심 기관 관련 스키마
# =================================

# class InterestOrganization(BaseSchema):
#     """관심 기관 정보"""
#     organization_id: int
#     organization_name: str
#     organization_description: str
#     registered_at: datetime

# class UserInterestListData(BaseModel):
#     """관심 기관 목록 데이터"""
#     interests: List[InterestOrganization]

# class UserInterestListResponse(BaseResponse):
#     """관심 기관 목록 응답"""
#     data: UserInterestListData

# class UserInterestUpdateRequest(BaseModel):
#     """관심 기관 추가/삭제 요청"""
#     organization_id: int
#     action: str = Field(..., regex="^(add|remove)$")

# class UserInterestUpdateData(BaseModel):
#     """관심 기관 수정 응답 데이터"""
#     interests: List[InterestOrganization]

# class UserInterestUpdateResponse(BaseResponse):
#     """관심 기관 수정 응답"""
#     message: str
#     data: UserInterestUpdateData
