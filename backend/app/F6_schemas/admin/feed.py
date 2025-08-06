from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationQuery, PaginationInfo, Settings

# ============================================================================
# 1. 피드 관련 열거형
# ============================================================================

class ProcessingStatus(str, Enum):
    """피드 처리 상태"""
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class ContentType(str, Enum):
    """콘텐츠 타입"""
    PDF = "pdf"
    TEXT = "text"

class FeedStatus(str, Enum):
    """피드 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"

# ============================================================================
# 2. 피드 스키마
# ============================================================================

class FeedListItem(BaseSchema):
    """피드 목록 항목"""
    id: int
    title: str
    organization_id: int
    organization_name: str
    category_name: str
    status: FeedStatus
    #processing_status: ProcessingStatus
    view_count: int
    created_at: datetime

class FeedDetail(BaseSchema):
    """피드 상세 정보"""
    id: int
    organization_id: int
    organization_name: str
    category_id: int
    category_name: str
    title: str
    summary: Optional[str]
    original_text: Optional[str]
    # pdf_file_path: Optional[str] # 아래 pdf_url로 대체
    source_url: str
    published_date: datetime
    is_active: bool
    # processing_status는 나중에 추가
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    # --- 💡 새로운 필드 추가 및 수정 💡 ---
    content_type: ContentType # "pdf" 또는 "text"
    pdf_url: Optional[str] = None # PDF 타입일 때만 값이 있음

class FeedCreateResult(BaseSchema):
    """피드 생성 결과"""
    id: int
    title: str
    processing_status: ProcessingStatus
    estimated_completion: datetime

class FeedUpdateResult(BaseSchema):
    """피드 수정 결과"""
    id: int
    title: str
    organization_name: str
    category_name: str
    updated_at: datetime

class DeactivatedFeedItem(BaseSchema):
    """비활성화된 피드 항목"""
    id: int
    title: str
    organization_name: str
    category_name: str
    deactivated_at: datetime

class OrganizationCategory(BaseSchema):
    """기관별 카테고리"""
    id: int
    name: str
    is_active: bool

# ============================================================================
# 3. 요청 스키마
# ============================================================================

class FeedListRequest(PaginationQuery):
    """피드 목록 조회 요청"""
    search: Optional[str] = Field(None, description="검색어")
    organization_id: Optional[int] = Field(None, description="기관 ID 필터")
    category_id: Optional[int] = Field(None, description="카테고리 ID 필터")

    # 피드 관리에서는 50개씩 보는게 기본
    limit: int = Field(default=50, ge=1, le=50, description="페이지당 항목 수")

class DeactivatedFeedListRequest(PaginationQuery):
    """비활성화된 피드 목록 조회 요청"""
    limit: int = Field(default=50, ge=1, le=50, description="페이지당 항목 수")

class FeedCreateRequest(BaseModel):
    """피드 생성 요청"""
    title: str = Field(..., description="피드 제목")
    organization_id: int = Field(..., description="기관 ID")
    category_id: int = Field(..., description="카테고리 ID")
    source_url: str = Field(..., description="원본 콘텐츠 URL")
    published_date: str = Field(..., description="발행 일시 (YYYY-MM-DD)")
    content_type: ContentType = Field(..., description="콘텐츠 타입")
    original_text: Optional[str] = Field(None, description="원본 텍스트")

class FeedUpdateRequest(BaseModel):
    """피드 수정 요청"""
    title: str = Field(..., description="피드 제목")
    organization_id: int = Field(..., description="기관 ID")
    category_id: int = Field(..., description="카테고리 ID")
    summary: Optional[str] = Field(None, description="요약문")
    original_text: Optional[str] = Field(None, description="원본 텍스트")
    source_url: str = Field(..., description="원본 URL")
    is_active: bool = Field(True, description="활성화 여부")

# ============================================================================
# 4. 응답 스키마
# ============================================================================

class FeedListData(BaseSchema):
    """피드 목록 데이터"""
    feeds: List[FeedListItem]
    pagination: PaginationInfo

class FeedListResponse(BaseResponse):
    """피드 목록 응답"""
    success: bool = True
    data: FeedListData

class FeedDetailResponse(BaseResponse):
    """피드 상세 응답"""
    success: bool = True
    data: FeedDetail

class FeedCreateResponse(BaseResponse):
    """피드 생성 응답"""
    success: bool = True
    message: str = "피드 생성 요청이 접수되었습니다. 처리 완료까지 약 5분이 소요됩니다."
    data: FeedCreateResult

class FeedUpdateResponse(BaseResponse):
    """피드 수정 응답"""
    success: bool = True
    data: FeedUpdateResult

class FeedDeactivateResponse(BaseResponse):
    """피드 비활성화 응답"""
    success: bool = True
    message: str = "피드가 비활성화되었습니다."

class DeactivatedFeedListData(BaseSchema):
    """비활성화된 피드 목록 데이터"""
    feeds: List[DeactivatedFeedItem]
    pagination: PaginationInfo

class DeactivatedFeedListResponse(BaseResponse):
    """비활성화된 피드 목록 응답"""
    success: bool = True
    data: DeactivatedFeedListData

class FeedDeleteResponse(BaseResponse):
    """피드 완전 삭제 응답"""
    success: bool = True
    message: str = "피드가 완전히 삭제되었습니다."

class OrganizationCategoriesResponse(BaseResponse):
    """기관별 카테고리 응답"""
    success: bool = True
    data: List[OrganizationCategory]

# ============================================================================
# 5. 경로 파라미터 스키마
# ============================================================================

class FeedPathParams(BaseModel):
    """피드 경로 파라미터"""
    id: int = Field(..., ge=1, description="피드 ID")

class OrganizationPathParams(BaseModel):
    """기관 경로 파라미터"""
    organization_id: int = Field(..., ge=1, description="기관 ID")

# ============================================================================
# 6. 유틸리티 함수(Service 레이어에서 검증 시 사용 X)
# ============================================================================

def is_processing_complete(status: ProcessingStatus) -> bool:
    """처리 완료 여부 확인"""
    return status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]

def get_estimated_completion_time() -> datetime:
    """예상 완료 시간 계산"""
    from datetime import datetime, timedelta
    return datetime.utcnow() + timedelta(minutes=Settings.ESTIMATED_PROCESSING_TIME)

def validate_content_request(content_type: ContentType, pdf_file: Optional[str], original_text: Optional[str]) -> bool:
    """콘텐츠 요청 유효성 검증"""
    if content_type == ContentType.PDF:
        return pdf_file is not None and original_text is None
    elif content_type == ContentType.TEXT:
        return original_text is not None and pdf_file is None
    return False
