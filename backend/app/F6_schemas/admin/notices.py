from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, model_validator
from enum import Enum

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse

# =======================
# 1. 공지사항 관련 열거형
# =======================
class NoticeStatus(str, Enum):
    """공지사항 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"

# =======================
# 2. 공지사항 스키마
# =======================

class NoticeListItem(BaseSchema):
    """공지사항 목록 항목"""
    id: int
    title: str
    content: str
    author: str
    is_pinned: bool
    is_active: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

class NoticeDetail(BaseSchema):
    """공지사항 상세 정보"""
    id: int
    title: str
    content: str
    author: str
    is_pinned: bool
    is_active: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# =======================
# 3. 요청 스키마
# =======================

class NoticeCreateRequest(BaseModel):
    """공지사항 생성 요청"""
    title: str
    content: str
    is_active: bool

class NoticeUpdateRequest(BaseModel):
    """공지사항 수정 요청"""
    title: Optional[str] = None
    content: Optional[str] = None
    is_active: Optional[bool] = None

class NoticePinUpdateRequest(BaseModel):
    """공지사항 고정 상태 수정 요청"""
    is_pinned: bool

class NoticeStatusUpdateRequest(BaseModel):
    """공지사항 활성화 상태 수정 요청"""
    is_active: bool

class NoticePinStateUpdateRequest(BaseModel):
    """공지사항 고정 또는 활성화 상태 변경 (통합)"""
    is_pinned: Optional[bool] = None
    is_active: Optional[bool] = None

    # (선택적) 둘 다 안 보내는 것을 막는 유효성 검사
    @model_validator(mode='before')
    def check_at_least_one_field_is_provided(cls, data: Any) -> Any:
        """
        요청 본문에 적어도 하나의 필드가 있는지, 또는 빈 객체가 아닌지 확인합니다.
        """
        # data가 딕셔너리가 아니거나, 비어있는 딕셔너리라면 에러 발생
        if not isinstance(data, dict) or not data:
            raise ValueError("적어도 하나의 필드(is_pinned 또는 is_active)는 제공되어야 합니다.")
        return data

# =======================
# 4. 응답 스키마
# =======================

class NoticeListResponse(BaseResponse):
    """공지사항 목록 응답"""
    success: bool = True
    data: List[NoticeListItem]

class NoticeDetailResponse(BaseResponse):
    """공지사항 상세 응답"""
    success: bool = True
    data: NoticeDetail

class NoticeCreateResponse(BaseResponse):
    """공지사항 생성 응답"""
    success: bool = True
    data: NoticeDetail

class NoticeUpdateResponse(BaseResponse):
    """공지사항 수정 응답"""
    success: bool = True
    data: NoticeDetail

class NoticeDeleteResponse(BaseResponse):
    """공지사항 삭제 응답"""
    success: bool = True
    message: str = "공지사항이 성공적으로 삭제되었습니다."

# =======================
# 5. 경로 파라미터 스키마
# =======================

class NoticePathParams(BaseModel):
    """공지사항 경로 파라미터"""
    id: int = Field(..., gt=0, description="공지사항 ID (양의 정수)")

# =======================
# 6. 확장용 스키마 (향후 사용, 언젠가 먼 미래에)
# =======================

class NoticeFilter(BaseModel):
    """공지사항 필터링 (향후 검색 기능 추가 시 사용)"""
    is_pinned: Optional[bool] = None
    is_active: Optional[bool] = None
    author: Optional[str] = None