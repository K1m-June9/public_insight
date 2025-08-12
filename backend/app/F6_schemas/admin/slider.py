from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse

# ============================================================================
# 1. 슬라이더 관련 열거형
# ============================================================================

class SliderStatus(str, Enum):
    """슬라이더 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"

# ============================================================================
# 2. 슬라이더 스키마
# ============================================================================

class SliderListItem(BaseSchema):
    """슬라이더 목록 항목"""
    id: int
    title: str
    preview: str
    tag: str
    content: str
    author: str
    image_path: str
    display_order: int
    is_active: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None 

class SliderDetail(BaseSchema):
    """슬라이더 상세 정보"""
    id: int
    title: str
    preview: str
    tag: str
    content: str
    author: str
    image: str  # Base64 인코딩된 이미지
    display_order: int
    is_active: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class SliderStatusUpdateResponseData(BaseSchema):
    """슬라이더 활성 상태 변경 성공 시 응답 데이터"""
    id: int
    is_active: bool
    updated_at: datetime


# ============================================================================
# 3. 요청 스키마
# ============================================================================

class SliderCreateRequest(BaseModel):
    """슬라이더 생성 요청 (multipart/form-data)"""
    title: str
    preview: str
    tag: str
    content: str
    display_order: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # image는 multipart로 별도 처리

class SliderUpdateRequest(BaseModel):
    """슬라이더 수정 요청 (multipart/form-data)"""
    title: Optional[str] = None
    preview: Optional[str] = None
    tag: Optional[str] = None
    content: Optional[str] = None
    display_order: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    # image는 선택적으로 multipart로 별도 처리

class SliderStatusUpdateRequest(BaseModel):
    """슬라이더 상태 수정 요청"""
    is_active: bool

# ============================================================================
# 4. 응답 스키마
# ============================================================================

class SliderListResponse(BaseResponse):
    """슬라이더 목록 응답"""
    success: bool = True
    data: List[SliderListItem]

class SliderDetailResponse(BaseResponse):
    """슬라이더 상세 응답"""
    success: bool = True
    data: SliderDetail

class SliderCreateResponse(BaseResponse):
    """슬라이더 생성 응답"""
    success: bool = True
    data: SliderDetail

class SliderUpdateResponse(BaseResponse):
    """슬라이더 수정 응답"""
    success: bool = True
    data: SliderDetail

class SliderStatusUpdateResponse(BaseResponse):
    """슬라이더 활성 상태 변경 최종 응답"""
    success: bool = True 
    data: SliderStatusUpdateResponseData

class SliderDeleteResponse(BaseResponse):
    """슬라이더 삭제 응답"""
    success: bool = True
    message: str = "슬라이더가 성공적으로 삭제되었습니다."


# ============================================================================
# 5. 경로 파라미터 스키마
# ============================================================================

class SliderPathParams(BaseModel):
    """슬라이더 경로 파라미터"""
    id: int = Field(..., gt=0, description="슬라이더 ID (양의 정수)")

# ============================================================================
# 6. 확장용 스키마 (향후 사용)
# ============================================================================

class SliderFilter(BaseModel):
    """슬라이더 필터링 (향후 검색 기능 추가 시 사용)"""
    is_active: Optional[bool] = None
    tag: Optional[str] = None
    author: Optional[str] = None
