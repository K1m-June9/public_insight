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
    BAD_REQUEST = "BAD_REQUEST"
    DUPLICATE = "DUPLICATE"
    
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
    LOGIN_SUCCESS = "로그인에 성공했습니다"
    
    # 에러 메시지
    # ErrorCode.INVALID_
    INVALID_CREDENTIALS = "현재 비밀번호가 일치하지 않습니다."

    # ErrorCode.NOT_FOUND
    NOT_FOUND = "요청한 리소스를 찾을 수 없습니다"
    SLIDER_NOT_FOUND = "슬라이더를 찾을 수 없습니다."
    NOTICE_NOT_FOUND = "공지사항을 찾을 수 없습니다."
    PAGE_NOT_FOUND = "해당 페이지를 찾을 수 없습니다."
    USER_NOT_FOUND = "사용자를 찾을 수 없습니다."
    FEED_NOT_FOUND = "피드를 찾을 수 없습니다."
    ORGANIZATION_NOT_FOUND = "기관을 찾을 수 없습니다."
    CATEGORY_NOT_FOUND = "카테고리를 찾을 수 없습니다."

    # ErrorCode.DUPLICATE
    DUPLICATE_ORGANIZATION_NAME = "이미 존재하는 기관명입니다."
    DUPLICATE_CATEGORY_NAME = "해당 기관에 이미 존재하는 카테고리명입니다."
    DUPLICATE_NICKNAME = "이미 사용 중인 닉네임입니다."
    DUPLICATE_PASSWROD = "새 비밀번호는 기존 비밀번호와 달라야 합니다."

    #ErrorCode.ALEADY_EXIST
    RATING_ALEADY_EXIST = "이미 별점을 준 피드입니다"


    # ErrorCode.FORBIDDEN
    PROTECTED_CATEGORY_DELETE_ERROR = "보도자료 카테고리는 삭제할 수 없습니다."
    FORBIDDEN = "접근 권한이 없습니다"
    PINNED_NOTICE_DELETE_FORBIDDEN = "고정된 공지사항은 삭제할 수 없습니다."

    # ErrorCode.BAD_REQUEST
    MISSING_REQUIRED_FIELDS = "필수 필드가 누락되었습니다."
    INVALID_CONTENT_TYPE = "PDF 파일 또는 텍스트 중 하나만 제공해야 합니다."
    EMPTY_CONTENT_ERROR = "콘텐츠가 비어있습니다."


    # ErrorCode.UNAUTHORIZED
    UNAUTHORIZED = "인증이 필요합니다"
    
    # ErrorCode.INVALID_PARAMETER
    INVALID_PARAMETER = "잘못된 파라미터입니다"
    LOGIN_FAILED = "아이디 또는 비밀번호가 올바르지 않습니다"
    
    # ErrorCode.VALIDATION_ERROR
    INVALID_URL = "유효하지 않은 URL 형식입니다."
    INVALID_SLUG_ERROR = "유효하지 않은 페이지 슬러그입니다."
    INVALID_ROLE_CHANGE = "ADMIN 권한은 변경할 수 없습니다."
    INVALID_STATUS_ERROR = "유효하지 않은 상태값입니다."
    INVALID_RATING_SCORE = "별점은 1-5점 사이의 값이어야 합니다"
    
    # ErrorCode.VALIDATION_ERROR
    VALIDATION_ERROR = "입력값 검증에 실패했습니다."
    VALIDATION_PASSWORD = "비밀번호는 8자 이상, 영문, 숫자, 특수문자를 포함해야 합니다."

    # ErrorCode.INTERNAL_ERROR
    INTERNAL_ERROR = "서버 내부 오류가 발생했습니다."
    
    # ErrorCode.FILE_TOO_LARGE
    FILE_TOO_LARGE = "파일 크기가 너무 큽니다."

    # ErrorCode.INVALID_FILE_TYPE
    INVALID_FILE_TYPE = "지원하지 않는 파일 형식입니다."

    # ErrorCode.FILE_UPLOAD_FAILED
    FILE_UPLOAD_FAILED = "파일 업로드에 실패했습니다."

    # ErrorCode.CONFLICT
    PROCESSING_IN_PROGRESS = "현재 처리 중입니다. 완료 후 다시 시도해주세요."

# ============================================================================
# 14. 설정 상수
# ============================================================================

class Settings:
    """공통 설정 상수"""
    # 페이지네이션(기본)
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # 페이지네이션(사용자 관리, 피드 관리)
    PAGE_SIZE_50 = 50
    MAX_PAGE_SIZE_50 = 50
    
    # 최대 이미지 크기
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # 최대 PDF 크기
    MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB

    # 업로드 가능한 이미지 타입
    ALLOWED_IMAGE_TYPES = [
        'image/jpeg', 'image/jpg', 'image/png',
        'image/gif', 'image/svg+xml', 'image/tiff'
    ]
    
    # 업로드 가능한 정책 및 보도자료 파일 타입(PDF 제외 불가)
    ALLOWED_DOCUMENT_TYPES = ["application/pdf"]

    # 업로드 가능한 아이콘 타입(일반 이미지와 별도)
    ALLOWED_ICON_EXTENSIONS = ['.ico', '.svg']

    # 허용 가능한 pdf 확장자
    ALLOWED_PDF_EXTENSIONS = ['.pdf']

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
    
    """대시보드 관련 설정"""
    # 데이터 제한
    MAX_POPULAR_KEYWORDS = 10
    MAX_ORGANIZATION_STATS = 5
    MAX_TOP_FEEDS = 3
    MAX_RECENT_ACTIVITIES = 10
    
    # 기간 설정
    MONTHLY_SIGNUPS_DAYS = 90  # 90일간의 일별 가입자 통계
    
    # 캐시 설정 (향후 적용 시)
    CACHE_TTL_DASHBOARD = 300  # 5분
    
    # 활동 로그 보관 기간(일)
    ACTIVITY_LOG_RETENTION_DAYS = 30
    
    """슬라이더 관련 설정"""
    # 표시 순서 설정
    MIN_DISPLAY_ORDER = 0
    INACTIVE_DISPLAY_ORDER = -1
    # 파일 업로드(backend/app/static/sliders/{UUID})
    SLIDER_UPLOADS_PATH = "static/sliders"

    # 정렬 기준
    DEFAULT_SORT = "is_active ASC, display_order ASC"
    
    """공지사항 관련 설정"""
    # 정렬 기준
    DEFAULT_SORT = "is_pinned DESC, created_at DESC"
    
    """정적 페이지 관련 설정"""
    # 고정 페이지 정보
    FIXED_PAGES = {
        "about": "프로젝트 소개",
        "terms": "이용 약관",
        "privacy": "개인정보처리방침",
        "youth-protection": "청소년 보호 정책"
    }

    # 허용된 슬러그 목록
    ALLOWED_SLUGS = ["about", "terms", "privacy", "youth-protection"]

    # 콘텐츠 관련
    MIN_CONTENT_LENGTH = 1
    DEFAULT_CONTENT_TYPE = "markdown"
    
    # 실제 파일이 저장될 '서버 컴퓨터의 물리적 경로'
    # pdf 저장할 때 DB: pdf_file_path = {UUID}
    #    (파일을 '저장'할 때 사용)
    PDF_STORAGE_PATH = "static/feeds_pdf"

    # 웹 브라우저가 접근할 'URL 상의 기본 경로'
    #    (URL을 '생성'할 때 사용)
    STATIC_FILES_URL = "/static"

    # 처리 시간
    ESTIMATED_PROCESSING_TIME = 5  # 분
    PROCESSING_TIMEOUT = 30  # 분

    # 검색 설정
    SEARCH_FIELDS = ["title"]
    
    """기관/카테고리 관련 상수"""
    # 보호 카테고리
    PROTECTED_CATEGORY_NAME = "보도자료"

    # 파일 업로드(backend/app/organization_icon/{UUID})
    ICON_UPLOAD_PATH = "/organization_icon/"