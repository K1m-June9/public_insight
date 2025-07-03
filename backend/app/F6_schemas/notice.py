from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationInfo


# =================================
# 1. 고정 공지사항 관련 스키마
# =================================

class PinnedNoticeItem(BaseSchema):
    """고정 공지사항 항목"""
    id: int
    title: str
    created_at: datetime

class PinnedNoticeData(BaseModel):
    """고정 공지사항 데이터"""
    notices: List[PinnedNoticeItem]
    count: int

class PinnedNoticeResponse(BaseResponse):
    """고정 공지사항 응답"""
    data: PinnedNoticeData

# =================================
# 2. 공지사항 목록 관련 스키마
# =================================

class NoticeListItem(BaseSchema):
    """공지사항 목록 항목"""
    id: int
    title: str
    author: str
    is_pinned: bool
    created_at: datetime

class NoticeListData(BaseModel):
    """공지사항 목록 데이터"""
    notices: List[NoticeListItem]
    pagination: PaginationInfo

class NoticeListResponse(BaseResponse):
    """공지사항 목록 응답"""
    data: NoticeListData

class NoticeListQuery(BaseModel):
    """공지사항 목록 쿼리 파라미터"""
    page: int = Field(default=1, ge=1, description="페이지 번호 (1부터 시작)")
    limit: int = Field(default=20, ge=1, le=100, description="페이지당 항목 수 (최대 100)")

# =================================
# 3. 공지사항 상세 관련 스키마
# =================================

class NoticeDetail(BaseSchema):
    """공지사항 상세 정보"""
    id: int
    title: str
    author: str
    content: str
    is_pinned: bool
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime]  

class NoticeDetailData(BaseModel):
    """공지사항 상세 데이터"""
    notice: NoticeDetail

class NoticeDetailResponse(BaseResponse):
    """공지사항 상세 응답"""
    data: NoticeDetailData
# =================================
# 4. 경로 파라미터 스키마
# =================================

class NoticePathParams(BaseModel):
    """공지사항 경로 파라미터"""
    id: int = Field(..., gt=0, description="공지사항 ID (양의 정수)")
