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
    feed_count: int

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
    iconURL: str  # Base64 -> URL 방식으로 변경

class OrganizationIconData(BaseModel):
    """기관 아이콘 데이터"""
    organization: OrganizationWithIcon

class OrganizationIconResponse(BaseResponse):
    """기관 아이콘 응답"""
    data: OrganizationIconData

# ============================================================================
# 4. 워드클라우드 관련 스키마
# ============================================================================

class WordCloudKeywordItem(BaseSchema):
    """워드클라우드에 표시될 개별 키워드 항목"""
    text: str = Field(..., description="키워드 텍스트")
    size: int = Field(..., description="계산된 글자 크기")
    color: str = Field(..., description="랜덤하게 할당된 글자 색상 (HEX 코드)")
    weight: int = Field(..., description="계산된 글자 굵기 (font-weight)")

class WordCloudData(BaseSchema): # 기존 WordCloudData 스키마와 이름이 겹치므로 확인 필요
    """기관별 워드클라우드 데이터"""
    organization: OrganizationInfo
    keywords: List[WordCloudKeywordItem]

class WordCloudResponse(BaseResponse):
    """기관별 워드클라우드 응답"""
    data: WordCloudData

# ============================================================================
# 6. 경로 파라미터 스키마
# ============================================================================

class OrganizationPathParams(BaseModel):
    """기관명 경로 파라미터"""
    organization_name: str = Field(..., min_length=1, description="기관명 (URL 디코딩 필요)")


# ============================================================================
# 7. UI 개편하면서 새로 만든 기관 페이지 헤더를 위한 스키마
# ============================================================================
# 파일 위치: backend/app/F6_schemas/organization.py

class OrganizationStats(BaseModel):
    documents: int
    views: int
    satisfaction: float

class OrganizationSummaryData(BaseSchema):
    id: int
    name: str
    description: str
    website_url: Optional[str] = None # 웹사이트 URL도 함께 보내주면 유용하지만 쓸까말까쓸까말까쓸래말래쓸래말래
    stats: OrganizationStats

class OrganizationSummaryResponse(BaseResponse):
    data: OrganizationSummaryData
