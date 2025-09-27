from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession 

from app.F2_services.admin.app_settings import AppSettingService
from app.F3_repositories.admin.app_settings import AppSettingRepository
from app.F5_core.config import settings
from app.F5_core.dependencies import get_admin_app_setting_service
from app.F6_schemas.admin.app_settings import (
    AppSettingCreateRequest,
    AppSettingUpdateRequest, 
    AppSettingResponse, 
    AppSettingDeleteResponse,
)


from app.F6_schemas.base import ErrorResponse, ErrorCode


router = APIRouter(tags=["Admin-App Settings"], prefix="/app-settings")


def handle_error_response(result: ErrorResponse) -> JSONResponse:
    """
    서비스 레이어로부터 받은 ErrorResponse 객체를 적절한 HTTP 상태코드와 함께 JSONResponse로 변환
    """
    status_code_map = {
        ErrorCode.BAD_REQUEST: 400,
        ErrorCode.UNAUTHORIZED: 401,
        ErrorCode.FORBIDDEN: 403,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.DUPLICATE: 409,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    status_code = status_code_map.get(result.error.code, 500)

    return JSONResponse(
        status_code=status_code,
        content=result.model_dump()
    )



# [POST] 새로운 설정 생성
@router.post("/", response_model=AppSettingResponse)
async def create_app_setting(
    request: Request,
    setting_data: AppSettingCreateRequest=Depends(),
    service: AppSettingService = Depends(get_admin_app_setting_service)
):
    result = await service.create_setting(setting_in=setting_data)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result 


# [GET] 단일 설정 조회
@router.get("/{key_name}", response_model=AppSettingResponse)
async def get_app_setting(
    key_name: str, 
    service: AppSettingService = Depends(get_admin_app_setting_service)
):
    result = await service.get_app_setting(key_name)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result 


# [PUT] 단일 설정 업데이트
@router.put("/{key_name}", response_model=AppSettingResponse)
async def update_app_setting(
    request: Request,
    setting_data: AppSettingUpdateRequest = Depends(), 
    service: AppSettingService = Depends(get_admin_app_setting_service)
):
    result = await service.update_setting(key_name=setting_data.key_name, setting_in=setting_data)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result 


# [DELETE] 단일 설정 삭제
@router.delete("/{key_name}", response_model=AppSettingDeleteResponse)
async def delete_app_setting(
    key_name: str,
    service: AppSettingService = Depends(get_admin_app_setting_service)
):
    result = await service.delete_setting(key_name)
    
    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result


