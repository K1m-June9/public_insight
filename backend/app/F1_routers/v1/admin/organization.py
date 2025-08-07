import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.F2_services.admin.organization import OrganizationAdminService
from app.F5_core.dependencies import get_admin_organization_service, verify_active_user
from app.F6_schemas.admin.organization import SimpleOrganizationListResponse, OrganizationListResponse
from app.F6_schemas.base import ErrorResponse
from app.F7_models.users import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Admin-Organizations"], prefix="/organizations")

#기존 계획에 없던 API
@router.get("/list", response_model=SimpleOrganizationListResponse)
async def get_simple_organization_list(
    admin_service: OrganizationAdminService = Depends(get_admin_organization_service),
    current_user: User = Depends(verify_active_user)
):
    result = await admin_service.get_simple_list()
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    return result

@router.get("", response_model=OrganizationListResponse)
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