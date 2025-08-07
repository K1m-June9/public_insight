from app.F6_schemas.base import BaseSchema, BaseResponse
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator

# base 스키마에서 필요한 클래스들 임포트
from app.F6_schemas.base import BaseSchema, BaseResponse

# 기존 계획에 없던 건데 필요해서 새로 생성한 스키마(관리자 피드 리스트 확인 시 기관 확인)
#======================================================
class SimpleOrganizationItem(BaseSchema):
    """관리자 필터링용 기관 정보 (ID와 이름만 포함)"""
    id: int
    name: str

class SimpleOrganizationListResponse(BaseResponse):
    """관리자 필터링용 기관 목록 응답"""
    data: List[SimpleOrganizationItem]

#======================================================


# ============================================================================
# 1. 기관/카테고리 스키마
# ============================================================================

class CategoryItem(BaseSchema):
    """카테고리 항목"""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

class OrganizationWithCategories(BaseSchema):
    """카테고리를 포함한 기관"""
    id: int
    name: str
    description: Optional[str]
    website_url: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    categories: List[CategoryItem]

class OrganizationDetail(BaseSchema):
    """기관 상세 정보"""
    id: int
    name: str
    description: Optional[str]
    website_url: Optional[str]
    icon_path: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

class CategoryDetail(BaseSchema):
    """카테고리 상세 정보"""
    id: int
    organization_id: int
    organization_name: str
    name: str
    description: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

class OrganizationCreateResult(BaseSchema):
    """기관 생성 결과"""
    id: int
    name: str
    description: Optional[str]
    website_url: Optional[str]
    icon_path: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    categories: List[CategoryItem]

class CategoryCreateResult(BaseSchema):
    """카테고리 생성 결과"""
    id: int
    organization_id: int
    organization_name: str
    name: str
    description: Optional[str]
    is_active: bool
    feed_count: int
    created_at: datetime
    updated_at: Optional[datetime]

# ============================================================================
# 2. 요청 스키마
# ============================================================================

class OrganizationCreateRequest(BaseModel):
    """기관 생성 요청"""
    name: str = Field(..., description="기관명")
    description: Optional[str] = Field(None, description="기관 설명")
    website_url: Optional[str] = Field(None, description="웹사이트 URL")
    is_active: bool = Field(True, description="활성화 상태")

    @validator('website_url')
    def validate_website_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('유효하지 않은 URL 형식입니다.')
        return v

class OrganizationUpdateRequest(BaseModel):
    """기관 수정 요청"""
    name: str = Field(..., description="기관명")
    description: Optional[str] = Field(None, description="기관 설명")
    website_url: Optional[str] = Field(None, description="웹사이트 URL")
    is_active: bool = Field(..., description="활성화 상태")

    @validator('website_url')
    def validate_website_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('유효하지 않은 URL 형식입니다.')
        return v

class CategoryCreateRequest(BaseModel):
    """카테고리 생성 요청"""
    organization_id: int = Field(..., description="기관 ID")
    name: str = Field(..., description="카테고리명")
    description: Optional[str] = Field(None, description="카테고리 설명")
    is_active: bool = Field(True, description="활성화 상태")

class CategoryUpdateRequest(BaseModel):
    """카테고리 수정 요청"""
    organization_id: int = Field(..., description="기관 ID")
    name: str = Field(..., description="카테고리명")
    description: Optional[str] = Field(None, description="카테고리 설명")
    is_active: bool = Field(..., description="활성화 상태")

# ============================================================================
# 3. 응답 스키마
# ============================================================================

class OrganizationListResponse(BaseResponse):
    """기관 목록 응답"""
    success: bool = True
    data: List[OrganizationWithCategories]

class OrganizationDetailResponse(BaseResponse):
    """기관 상세 응답"""
    success: bool = True
    data: OrganizationDetail

class OrganizationCreateResponse(BaseResponse):
    """기관 생성 응답"""
    success: bool = True
    data: OrganizationCreateResult

class OrganizationUpdateResponse(BaseResponse):
    """기관 수정 응답"""
    success: bool = True
    data: OrganizationDetail

class OrganizationDeleteResponse(BaseResponse):
    """기관 삭제 응답"""
    success: bool = True
    message: str = "기관이 성공적으로 삭제되었습니다."

class CategoryDetailResponse(BaseResponse):
    """카테고리 상세 응답"""
    success: bool = True
    data: CategoryDetail

class CategoryCreateResponse(BaseResponse):
    """카테고리 생성 응답"""
    success: bool = True
    data: CategoryCreateResult

class CategoryUpdateResponse(BaseResponse):
    """카테고리 수정 응답"""
    success: bool = True
    data: CategoryDetail

class CategoryDeleteResponse(BaseResponse):
    """카테고리 삭제 응답"""
    success: bool = True
    message: str = "카테고리가 성공적으로 삭제되었습니다."

# ============================================================================
# 4. 경로 파라미터 스키마
# ============================================================================

class OrganizationPathParams(BaseModel):
    """기관 경로 파라미터"""
    id: int = Field(..., ge=1, description="기관 ID")

class CategoryPathParams(BaseModel):
    """카테고리 경로 파라미터"""
    id: int = Field(..., ge=1, description="카테고리 ID")