from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse

# ============================================================================
# 1. 정적 페이지 관련 열거형
# ============================================================================

class StaticPageSlug(str, Enum):
    """정적 페이지 슬러그"""
    ABOUT = "about"
    TERMS = "terms"
    PRIVACY = "privacy"
    YOUTH_PROTECTION = "youth-protection"

# ============================================================================
# 2. 정적 페이지 스키마
# ============================================================================

class StaticPageListItem(BaseSchema):
    """정적 페이지 목록 항목"""
    id: int
    slug: str
    title: str
    created_at: datetime
    updated_at: datetime

class StaticPageDetail(BaseSchema):
    """정적 페이지 상세 정보"""
    id: int
    slug: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

# ============================================================================
# 3. 요청 스키마
# ============================================================================

class StaticPageUpdateRequest(BaseModel):
    """정적 페이지 수정 요청"""
    content: str

# ============================================================================
# 4. 응답 스키마
# ============================================================================

class StaticPageListResponse(BaseResponse):
    """정적 페이지 목록 응답"""
    success: bool = True
    data: List[StaticPageListItem]

class StaticPageDetailResponse(BaseResponse):
    """정적 페이지 상세 응답"""
    success: bool = True
    data: StaticPageDetail

class StaticPageUpdateResponse(BaseResponse):
    """정적 페이지 수정 응답"""
    success: bool = True
    data: StaticPageDetail

# ============================================================================
# 5. 경로 파라미터 스키마
# ============================================================================

class StaticPagePathParams(BaseModel):
    """정적 페이지 경로 파라미터"""
    slug: str = Field(..., description="페이지 슬러그")
