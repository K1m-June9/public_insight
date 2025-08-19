import logging
import json 

from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, Body, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, Dict, Any
from datetime import date
from pydantic import ValidationError

from app.F2_services.admin.notices import NoticesAdminService
from app.F5_core.config import settings
from app.F5_core.dependencies import verify_active_user, get_admin_notices_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.base import ErrorResponse, ErrorCode, PaginationQuery

from app.F6_schemas.admin.notices import (
    NoticeStatus,
    NoticeListItem,
    NoticeDetail,
    NoticeCreateRequest,
    NoticeUpdateRequest,
    NoticePinUpdateRequest,
    NoticeStatusUpdateRequest,
    NoticeListResponse,
    NoticeDetailResponse,
    NoticeCreateResponse,
    NoticeUpdateResponse,
    NoticeDeleteResponse,
    NoticePathParams,
    NoticePinStateUpdateRequest
)
from app.F7_models.notices import Notice
from app.F7_models.users import User


logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin-Notices"], prefix="/notices")

def handle_error_response(result: ErrorResponse) -> JSONResponse:
    """
    서비스 레이어로부터 받은 ErrorResponse 객체를 적절한 HTTP 상태코드와 함께 JSONResponse로 변환
    """
    status_code_map = {
        ErrorCode.BAD_REQUEST: 400,
        ErrorCode.FORBIDDEN: 403,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    status_code = status_code_map.get(result.error.code, 500)

    return JSONResponse(
        status_code=status_code,
        content=result.model_dump()
    )

# 모든 공지사항 목록 조회
@router.get("", response_model=NoticeListResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "NOTICE_MANAGEMENT"])
async def get_notice_list(
    request:Request,
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    result = await admin_service.get_notice_list(current_user)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result

# 공지사항 상세 조회
@router.get("/{id}", response_model=NoticeDetailResponse)
@log_event_detailed(action="READ", category=["ADMIN", "NOTICE_MANAGEMENT", "DETAIL"])
async def get_notice_detail(
    requet:Request,
    path_params: NoticePathParams = Depends(),
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    result = await admin_service.get_notice_detail(
        current_user=current_user, 
        notice_id=path_params.id
    ) 

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result


# 공지사항 생성
@router.post("", response_model=NoticeCreateResponse)
@log_event_detailed(action="CREATE", category=["ADMIN", "NOTICE_MANAGEMENT"])
async def create_notice(
    requet:Request,
    request_data: NoticeCreateRequest = Depends(),
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    """새로운 공지사항 생성"""
    result = await admin_service.create_notice(
        current_user=current_user,
        request_data=request_data
        )

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result



# 공지사항 수정
@router.put("/{id}", response_model=NoticeUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "NOTICE_MANAGEMENT"])
async def update_notice(
    requet:Request,
    request_data: NoticeUpdateRequest,
    path_params: NoticePathParams = Depends(),
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    """기존 슬라이더의 정보를 수정"""
    result = await admin_service.update_notice(
        current_user=current_user,
        notice_id=path_params.id,
        request_data=request_data
        )

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result

# 일단 통합해서 만듦
# 공지사항 부분수정(고정, 활성/비활성)
@router.patch("/{id}", response_model=NoticeUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "NOTICE_MANAGEMENT", "STATUS"])
async def update_notice_status(
    request:Request,
    request_data:NoticePinStateUpdateRequest,
    path_params: NoticePathParams = Depends(),
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    result = await admin_service.update_notice_status(
        current_user=current_user, 
        notice_id=path_params.id,
        request_data=request_data
    ) 

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result
    

# 공지사항 삭제
@router.delete("/{id}", response_model=NoticeDeleteResponse)
@log_event_detailed(action="DELETE", category=["ADMIN", "NOTICE_MANAGEMENT"])
async def delete_notice(
    requet:Request,
    path_params: NoticePathParams = Depends(),
    current_user: User = Depends(verify_active_user),
    admin_service: NoticesAdminService = Depends(get_admin_notices_service),
):
    result = await admin_service.delete_notice(
        current_user=current_user, 
        notice_id=path_params.id
    ) 

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result
