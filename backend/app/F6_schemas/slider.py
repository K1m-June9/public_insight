from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

from app.F6_schemas.base import BaseSchema, BaseResponse

# ============================================================================
# 1. 슬라이더 목록 관련 스키마
# ============================================================================

class SliderListItem(BaseSchema):
    """슬라이더 목록 항목"""
    id: int
    title: str
    preview: str
    imageURL: str  # Base64 -> URL 방식으로 변경
    display_order: int
    created_at: datetime

class SliderListData(BaseModel):
    """슬라이더 목록 데이터"""
    sliders: List[SliderListItem]

class SliderListResponse(BaseResponse):
    """슬라이더 목록 응답"""
    data: SliderListData

# ============================================================================
# 2. 슬라이더 상세 관련 스키마
# ============================================================================

class SliderDetail(BaseSchema):
    """슬라이더 상세 정보"""
    id: int
    title: str
    content: str  
    imageURL: str    # Base64 -> URL 방식으로 변경
    author: str
    tag: str
    created_at: datetime

class SliderDetailData(BaseModel):
    """슬라이더 상세 데이터"""
    slider: SliderDetail

class SliderDetailResponse(BaseResponse):
    """슬라이더 상세 응답"""
    data: SliderDetailData

# ============================================================================
# 3. 경로 파라미터 스키마
# ============================================================================

class SliderPathParams(BaseModel):
    """슬라이더 경로 파라미터"""
    id: int = Field(..., gt=0, description="슬라이더 ID (양의 정수)")
