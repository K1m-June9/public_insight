from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date

from app.F6_schemas.base import BaseSchema, BaseResponse

# ============================================================================
# 1. 기관 목록 관련 스키마
# ============================================================================

class OrganizationListItem(BaseSchema):
    """기관 목록 항목"""
    id: int
    name: str
    percentage: float

class OrganizationListData(BaseModel):
    """기관 목록 데이터"""
    organizations: List[OrganizationListItem]
    total_percentage: float

class OrganizationListResponse(BaseResponse):
    """기관 목록 응답"""
    data: OrganizationListData

# ============================================================================
# 2. 기관별 카테고리 관련 스키마
# ============================================================================

class OrganizationInfo(BaseSchema):
    """기관 기본 정보"""
    id: int
    name: str

class CategoryItem(BaseSchema):
    """카테고리 항목"""
    id: int
    name: str
    percentage: float

class OrganizationCategoryData(BaseModel):
    """기관별 카테고리 데이터"""
    organization: OrganizationInfo
    categories: List[CategoryItem]
    total_percentage: float

class OrganizationCategoryResponse(BaseResponse):
    """기관별 카테고리 응답"""
    data: OrganizationCategoryData

# ============================================================================
# 3. 기관 아이콘 관련 스키마
# ============================================================================

class OrganizationWithIcon(BaseSchema):
    """아이콘 포함 기관 정보"""
    id: int
    name: str
    website_url: str #기관 웹사이트 url
    icon: str  # Base64 인코딩된 이미지 데이터

class OrganizationIconData(BaseModel):
    """기관 아이콘 데이터"""
    organization: OrganizationWithIcon

class OrganizationIconResponse(BaseResponse):
    """기관 아이콘 응답"""
    data: OrganizationIconData

# ============================================================================
# 4. 워드클라우드 관련 스키마
# ============================================================================

class WordItem(BaseSchema):
    """워드클라우드 단어 항목"""
    text: str
    value: int

class WordCloudPeriod(BaseSchema):
    """워드클라우드 기간 정보"""
    start_date: date
    end_date: date

class WordCloudByYear(BaseSchema):
    """연도별 워드클라우드"""
    year: int
    words: List[WordItem]
    period: WordCloudPeriod
    generated_at: datetime

class WordCloudData(BaseModel):
    """워드클라우드 데이터"""
    organization: OrganizationInfo
    wordclouds: List[WordCloudByYear]

class WordCloudResponse(BaseResponse):
    """워드클라우드 응답"""
    data: WordCloudData

# ============================================================================
# 5. 워드클라우드 데이터 없는 경우 스키마
# ============================================================================

class EmptyWordCloud(BaseSchema):
    """빈 워드클라우드"""
    words: List[WordItem]  # [{"text": "죄송합니다", "value": 100}]
    period: Optional[WordCloudPeriod] = None
    generated_at: Optional[datetime] = None

class EmptyWordCloudData(BaseModel):
    """빈 워드클라우드 데이터"""
    organization: OrganizationInfo
    wordcloud: EmptyWordCloud

class EmptyWordCloudResponse(BaseResponse):
    """빈 워드클라우드 응답"""
    data: EmptyWordCloudData

# ============================================================================
# 6. 경로 파라미터 스키마
# ============================================================================

class OrganizationPathParams(BaseModel):
    """기관명 경로 파라미터"""
    organization_name: str = Field(..., min_length=1, description="기관명 (URL 디코딩 필요)")
