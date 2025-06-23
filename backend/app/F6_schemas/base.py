from datetime import datetime, date
from typing import Optional, Dict, List, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ============================================================================
# 1. 기본 베이스 스키마
# ============================================================================

class BaseSchema(BaseModel):
    """모든 스키마의 기본 클래스"""
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
    )

class TimestampMixin(BaseModel):
    """생성/수정 시간 필드 믹스인"""
    created_at: datetime
    updated_at: datetime


class IDMixin(BaseModel):
    """ID 필드 믹스인"""
    id: int


class BaseEntity(BaseSchema, IDMixin, TimestampMixin):
    """ID와 타임스탬프를 포함한 기본 엔티티"""
    pass


# ============================================================================
# 2. 기본 응답 구조
# ============================================================================

class BaseResponse(BaseModel):
    """모든 API 응답의 기본 구조"""
    success: bool


class SuccessResponse(BaseResponse):
    """성공 응답 (데이터 없음)"""
    success: bool = True


class ErrorDetail(BaseModel):
    """에러 상세 정보"""
    code: str = Field(..., description="에러 코드")
    message: str = Field(..., description="에러 메시지")
    details: Optional[Dict[str, str]] = Field(default=None, description="상세 에러 정보")


class ErrorResponse(BaseResponse):
    """에러 응답"""
    success: bool = False
    error: ErrorDetail


class DataResponse(BaseResponse):
    """데이터를 포함한 성공 응답"""
    success: bool = True
    data: Any


# ============================================================================
# 3. 페이지네이션
# ============================================================================

class PaginationInfo(BaseModel):
    """페이지네이션 정보"""
    current_page: int = Field(..., ge=1, description="현재 페이지")
    total_pages: int = Field(..., ge=0, description="전체 페이지 수")
    total_count: int = Field(..., ge=0, description="전체 항목 수")
    limit: int = Field(..., ge=1, description="페이지당 항목 수")
    has_next: bool = Field(..., description="다음 페이지 존재 여부")
    has_previous: bool = Field(..., description="이전 페이지 존재 여부")


class PaginatedResponse(BaseResponse):
    """페이지네이션을 포함한 응답"""
    success: bool = True
    data: List[Any]
    pagination: PaginationInfo


class PaginationQuery(BaseModel):
    """페이지네이션 쿼리 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수")


# ============================================================================
# 4. 공통 열거형
# ============================================================================

class SortOrder(str, Enum):
    """정렬 순서"""
    ASC = "asc"
    DESC = "desc"


class CommonSortField(str, Enum):
    """공통 정렬 필드"""
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    ID = "id"
    NAME = "name"
    TITLE = "title"


class StatusType(str, Enum):
    """공통 상태 타입"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    DELETED = "deleted"


class ContentType(str, Enum):
    """콘텐츠 유형"""
    POLICY = "정책"
    PRESS_RELEASE = "보도자료"
    ANNOUNCEMENT = "공고"
    REPORT = "보고서"
    NEWS = "뉴스"


class UserRole(str, Enum):
    """사용자 역할"""
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class NoticeType(str, Enum):
    """공지사항 유형"""
    GENERAL = "일반"
    URGENT = "긴급"
    EVENT = "이벤트"
    MAINTENANCE = "점검"


# ============================================================================
# 5. 공통 유틸리티 스키마
# ============================================================================

class DateRange(BaseModel):
    """날짜 범위"""
    start_date: Optional[date] = Field(default=None, description="시작 날짜")
    end_date: Optional[date] = Field(default=None, description="종료 날짜")
    
    @field_validator('end_date')
    @classmethod
    def validate_date_range(cls, v, values):
        if v and values.get('start_date') and v < values['start_date']:
            raise ValueError('종료 날짜는 시작 날짜보다 늦어야 합니다')
        return v


class FileInfo(BaseModel):
    """파일 정보"""
    filename: str = Field(..., description="파일명")
    file_url: str = Field(..., description="파일 URL")
    file_size: Optional[int] = Field(default=None, description="파일 크기 (bytes)")
    content_type: Optional[str] = Field(default=None, description="파일 MIME 타입")


class ImageInfo(BaseModel):
    """이미지 정보"""
    image_url: str = Field(..., description="이미지 URL")
    alt_text: Optional[str] = Field(default=None, description="대체 텍스트")
    width: Optional[int] = Field(default=None, description="이미지 너비")
    height: Optional[int] = Field(default=None, description="이미지 높이")


class LinkInfo(BaseModel):
    """링크 정보"""
    url: str = Field(..., description="링크 URL")
    title: Optional[str] = Field(default=None, description="링크 제목")
    description: Optional[str] = Field(default=None, description="링크 설명")


# ============================================================================
# 6. 조직/기관 관련 공통 스키마
# ============================================================================

class OrganizationBasic(BaseSchema):
    """기관 기본 정보"""
    id: int
    name: str
    logo_url: Optional[str] = None


class CategoryBasic(BaseSchema):
    """카테고리 기본 정보"""
    id: int
    name: str


class OrganizationWithCategory(OrganizationBasic):
    """카테고리를 포함한 기관 정보"""
    categories: List[CategoryBasic] = []


# ============================================================================
# 7. 사용자 관련 공통 스키마
# ============================================================================

class UserBasic(BaseSchema):
    """사용자 기본 정보"""
    id: int
    username: str
    email: str
    profile_image_url: Optional[str] = None


class UserPublic(BaseSchema):
    """공개 사용자 정보"""
    id: int
    username: str
    profile_image_url: Optional[str] = None


# ============================================================================
# 8. 통계 관련 공통 스키마
# ============================================================================

class CountInfo(BaseModel):
    """개수 정보"""
    count: int = Field(..., ge=0, description="개수")


class StatItem(BaseModel):
    """통계 항목"""
    name: str = Field(..., description="항목명")
    count: int = Field(..., ge=0, description="개수")
    percentage: Optional[float] = Field(default=None, ge=0, le=100, description="비율 (%)")


class RatingInfo(BaseModel):
    """평점 정보"""
    average_rating: float = Field(..., ge=0, le=5, description="평균 평점")
    rating_count: int = Field(..., ge=0, description="평점 개수")


# ============================================================================
# 9. 검색 관련 공통 스키마
# ============================================================================

class SearchQuery(BaseModel):
    """기본 검색 쿼리"""
    q: Optional[str] = Field(default=None, max_length=100, description="검색 키워드")
    
    @field_validator('q')
    @classmethod
    def validate_search_query(cls, v):
        if v and len(v.strip()) == 0:
            return None
        return v


class SortQuery(BaseModel):
    """정렬 쿼리"""
    sort_field: str = Field(default="created_at", description="정렬 필드")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="정렬 순서")


# ============================================================================
# 10. 메타데이터 관련 스키마
# ============================================================================

class MetaInfo(BaseModel):
    """메타 정보"""
    title: Optional[str] = Field(default=None, description="제목")
    description: Optional[str] = Field(default=None, description="설명")
    keywords: Optional[List[str]] = Field(default=None, description="키워드")
    author: Optional[str] = Field(default=None, description="작성자")


class SEOInfo(BaseModel):
    """SEO 정보"""
    meta_title: Optional[str] = Field(default=None, max_length=60, description="메타 제목")
    meta_description: Optional[str] = Field(default=None, max_length=160, description="메타 설명")
    canonical_url: Optional[str] = Field(default=None, description="정규 URL")


# ============================================================================
# 11. 공통 검증 함수
# ============================================================================

def validate_korean_text(text: str) -> str:
    """한국어 텍스트 검증"""
    if not text or len(text.strip()) == 0:
        raise ValueError('텍스트는 비어있을 수 없습니다')
    return text.strip()


def validate_url(url: str) -> str:
    """URL 형식 검증"""
    if not url.startswith(('http://', 'https://', '/')):
        raise ValueError('올바른 URL 형식이 아닙니다')
    return url


def validate_email(email: str) -> str:
    """이메일 형식 검증"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('올바른 이메일 형식이 아닙니다')
    return email.lower()


# ============================================================================
# 12. 공통 에러 코드
# ============================================================================

class ErrorCode:
    """공통 에러 코드"""
    # 일반 에러
    INVALID_PARAMETER = "INVALID_PARAMETER"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    
    # 인증/권한 에러
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    
    # 리소스 에러
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # 서버 에러
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    EXTERNAL_SERVICE_ERROR = "EXTERNAL_SERVICE_ERROR"
    
    # 파일 관련 에러
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FILE_TYPE = "INVALID_FILE_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    
    # 검색 관련 에러
    SEARCH_ENGINE_ERROR = "SEARCH_ENGINE_ERROR"
    SEARCH_TIMEOUT = "SEARCH_TIMEOUT"


# ============================================================================
# 13. 공통 메시지
# ============================================================================

class Message:
    """공통 메시지"""
    # 성공 메시지
    SUCCESS = "성공적으로 처리되었습니다"
    CREATED = "성공적으로 생성되었습니다"
    UPDATED = "성공적으로 수정되었습니다"
    DELETED = "성공적으로 삭제되었습니다"
    LOGIN_SUCCESS = "로그인에 성공했습니다" # 추가
    
    # 에러 메시지
    NOT_FOUND = "요청한 리소스를 찾을 수 없습니다"
    UNAUTHORIZED = "인증이 필요합니다"
    FORBIDDEN = "접근 권한이 없습니다"
    INVALID_PARAMETER = "잘못된 파라미터입니다"
    VALIDATION_ERROR = "입력값 검증에 실패했습니다"
    INTERNAL_ERROR = "서버 내부 오류가 발생했습니다"
    LOGIN_FAILED = "아이디 또는 비밀번호가 올바르지 않습니다" # 추가
    
    # 파일 관련 메시지
    FILE_TOO_LARGE = "파일 크기가 너무 큽니다"
    INVALID_FILE_TYPE = "지원하지 않는 파일 형식입니다"
    FILE_UPLOAD_FAILED = "파일 업로드에 실패했습니다"


# ============================================================================
# 14. 설정 상수
# ============================================================================

class Settings:
    """공통 설정 상수"""
    # 페이지네이션
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 파일 업로드
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    ALLOWED_DOCUMENT_TYPES = ["application/pdf", "application/msword"]
    
    # 텍스트 길이 제한
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_CONTENT_LENGTH = 50000
    MAX_SEARCH_QUERY_LENGTH = 100
    
    # 평점
    MIN_RATING = 1
    MAX_RATING = 5
    
    # 캐시 TTL (초)
    CACHE_TTL_SHORT = 300      # 5분
    CACHE_TTL_MEDIUM = 1800    # 30분
    CACHE_TTL_LONG = 3600      # 1시간
