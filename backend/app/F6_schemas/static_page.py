from pydantic import BaseModel, Field
from enum import Enum

from app.F6_schemas.base import BaseSchema, BaseResponse

# ============================================================================
# 1. 정적 페이지 관련 스키마
# ============================================================================

class StaticPageContent(BaseSchema):
    """정적 페이지 콘텐츠"""
    slug: str
    content: str  # Markdown에서 변환된 HTML 문자열

class StaticPageData(BaseModel):
    """정적 페이지 데이터"""
    page: StaticPageContent

class StaticPageResponse(BaseResponse):
    """정적 페이지 응답"""
    data: StaticPageData

# ============================================================================
# 2. 경로 파라미터 스키마
# ============================================================================

class StaticPagePathParams(BaseModel):
    """정적 페이지 경로 파라미터"""
    slug: str = Field(
        ...,
        pattern="^[a-z-]+$",
        min_length=1,
        max_length=50,
        description="페이지 식별자 (영문 소문자, 하이픈만 허용)"
    )

# ============================================================================
# 3. 지원되는 Slug 열거형 (선택사항)
# ============================================================================

class SupportedSlug(str, Enum):
    """지원되는 정적 페이지 slug 목록"""
    ABOUT = "about"
    TERMS = "terms"
    PRIVACY = "privacy"
    YOUTH_PROTECTION = "youth-protection"
    INVALID_PAGE = "invalid-page"
