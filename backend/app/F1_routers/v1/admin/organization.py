import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from fastapi import Form
from typing import Optional

from app.F2_services.admin.organization import OrganizationAdminService
from app.F5_core.dependencies import get_admin_organization_service, verify_active_user
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.admin.organization import (
    SimpleOrganizationListResponse, 
    OrganizationListResponse, 
    OrganizationCreateResponse, 
    CategoryCreateRequest, 
    CategoryCreateResponse, 
    OrganizationUpdateResponse, 
    OrganizationUpdateRequest,
    CategoryDetailResponse,
    CategoryUpdateResponse,
    CategoryUpdateRequest,
    OrganizationDetailResponse,
    OrganizationDeleteResponse,
    CategoryDeleteResponse,
    OrganizationCreateRequest
    )
from app.F6_schemas.base import ErrorResponse, ErrorCode
from app.F7_models.users import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin-Organizations"], prefix="/organizations")

#기존 계획에 없던 API
@router.get("/list", response_model=SimpleOrganizationListResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "SIMPLE_LIST"])
async def get_simple_organization_list(
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    result = await admin_service.get_simple_list()
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    return result

@router.get("", response_model=OrganizationListResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "ORGANIZATION_MANAGEMENT"])
async def get_organizations_list(
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 모든 기관과 각 기관에 속한 카테고리 목록을 조회
    """
    result = await admin_service.get_organizations_list()

    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    return result

@router.post("", response_model=OrganizationCreateResponse, status_code=201)
@log_event_detailed(action="CREATE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "ORGANIZATION"])
async def create_organization(
    # multipart/form-data를 처리하기 위해 Form을 사용
    # 아이콘 파일이 없더라도, 텍스트 데이터를 form-data로 받는 것이 확장성에 유리
    request: Request,
    payload: OrganizationCreateRequest, 
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 새로운 기관을 생성
    생성 시 '보도자료' 카테고리가 자동으로 함께 생성
    """
    result = await admin_service.create_organization(
        name=payload.name,
        description=payload.description,
        website_url=payload.website_url,
        is_active=payload.is_active
    )

    if isinstance(result, ErrorResponse):
        status_code = 409 if result.error.code == ErrorCode.DUPLICATE else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.post("/categories", response_model=CategoryCreateResponse, status_code=201)
@log_event_detailed(action="CREATE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "CATEGORY"])
async def create_category(
    request: Request,
    payload: CategoryCreateRequest,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 새로운 카테고리를 생성
    """
    result = await admin_service.create_category(payload)

    if isinstance(result, ErrorResponse):
        status_code = 409 if result.error.code == ErrorCode.DUPLICATE else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.patch("/{id}", response_model=OrganizationUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "ORGANIZATION"])
async def update_organization(
    id: int,
    request: Request,
    payload: OrganizationUpdateRequest, # JSON Body로 받음
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 기관의 정보를 수정
    """
    # multipart/form-data가 아니므로, Pydantic 모델을 바로 사용
    result = await admin_service.update_organization(
        org_id=id,
        name=payload.name,
        description=payload.description,
        website_url=payload.website_url,
        is_active=payload.is_active
    )

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/categories/{id}", response_model=CategoryDetailResponse)
@log_event_detailed(action="READ", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "ORGANIZATION", "DETAIL"])
async def get_category_detail(
    id: int,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: ID로 특정 카테고리의 상세 정보를 조회
    """
    result = await admin_service.get_category_detail(id)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result

@router.patch("/categories/{id}", response_model=CategoryUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "CATEGORY"])
async def update_category(
    id: int,
    request: Request,
    payload: CategoryUpdateRequest,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 카테고리의 정보를 수정
    """
    result = await admin_service.update_category(id, payload)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result

@router.get("/{id}", response_model=OrganizationDetailResponse)
@log_event_detailed(action="READ", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "CATEGORY", "DETAIL"])
async def get_organization_detail(
    id: int,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: ID로 특정 기관의 상세 정보를 조회
    """
    result = await admin_service.get_organization_detail(id)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result

@router.delete("/{id}", response_model=OrganizationDeleteResponse)
@log_event_detailed(action="DELETE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "ORGANIZATION"])
async def delete_organization(
    id: int,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 기관을 삭제
    """
    result = await admin_service.delete_organization(id)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result

@router.delete("/categories/{id}", response_model=CategoryDeleteResponse)
@log_event_detailed(action="DELETE", category=["ADMIN", "ORGANIZATION_MANAGEMENT", "CATEGORY"])
async def delete_category(
    id: int,
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 카테고리를 삭제
    보도자료는 삭제 불가
    """
    result = await admin_service.delete_category(id)
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.FORBIDDEN:
            status_code = 403
        else:
            status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result