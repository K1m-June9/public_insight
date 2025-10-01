import logging
import json 

from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, Body, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, Dict, Any
from datetime import date
from pydantic import ValidationError

from app.F2_services.admin.slider import SliderAdminService
from app.F5_core.config import settings
from app.F5_core.dependencies import verify_active_user, get_admin_slider_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.base import ErrorResponse, ErrorCode, PaginationQuery

from app.F6_schemas.admin.slider import (
    SliderListResponse,
    SliderPathParams,
    SliderDetailResponse,
    SliderCreateResponse,
    SliderCreateRequest,
    SliderUpdateRequest,
    SliderUpdateResponse,
    SliderStatusUpdateResponse,
    SliderStatusUpdateRequest,
    SliderDeleteResponse,

)


from app.F7_models.sliders import Slider
from app.F7_models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin-Slider"], prefix="/slider")

def handle_error_response(result: ErrorResponse) -> JSONResponse:
    """
    서비스 레이어로부터 받은 ErrorResponse 객체를 적절한 HTTP 상태코드와 함께 JSONResponse로 변환
    """
    status_code_map = {
        ErrorCode.BAD_REQUEST: 400,
        ErrorCode.UNAUTHORIZED: 401,
        ErrorCode.FORBIDDEN: 403,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.FILE_TOO_LARGE: 413,
        ErrorCode.VALIDATION_ERROR: 422,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    status_code = status_code_map.get(result.error.code, 500)

    return JSONResponse(
        status_code=status_code,
        content=result.model_dump()
    )

class SliderCreateForm:
    def __init__(
        self,
        title: str = Form(...),
        preview: str = Form(...),
        tag: str = Form(...),
        content: str = Form(...),
        display_order: int = Form(...),
        start_date: Optional[date] = Form(None),
        end_date: Optional[date] = Form(None),
    ):
        self.model = SliderCreateRequest(
            title=title,
            preview=preview,
            tag=tag,
            content=content,
            display_order=display_order,
            start_date=start_date,
            end_date=end_date,
        )

@router.get("",response_model=SliderListResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "SLIDER_MANAGEMENT"])
async def get_slider_list(
    request:Request,
    # current_user: User = Depends(verify_active_user),
    admin_service: SliderAdminService = Depends(get_admin_slider_service),
):
    """모든 슬라이더 목록을 'display_order' 오름차순으로 정렬하여 반환"""
    # if current_user.role != UserRole.ADMIN:
    #     error_response = ErrorResponse(
    #         success=False,
    #         error=ErrorDetail(
    #             code=ErrorCode.FORBIDDEN,
    #             message=Message.FORBIDDEN

    #         )
    #     )
    #     return JSONResponse(
    #         status_code=403, content=error_response.model_dump()
    #     )
    result = await admin_service.get_slider_list()

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result 

@router.get("/{id}", response_model=SliderDetailResponse)
@log_event_detailed(action="READ", category=["ADMIN", "SLIDER_MANAGEMENT", "DETAIL"])
async def get_slider_detail(
    request:Request,
    path_params: SliderPathParams = Depends(),
    # current_user: User = Depends(verify_active_user),
    admin_service: SliderAdminService = Depends(get_admin_slider_service),
):
    """특정 슬라이더 목록의 상세 정보를 조회"""
    # if current_user.role != UserRole.ADMIN:
    #     error_response = ErrorResponse(
    #         success=False,
    #         error=ErrorDetail(
    #             code=ErrorCode.FORBIDDEN,
    #             message=Message.FORBIDDEN

    #         )
    #     )
    #     return JSONResponse(
    #         status_code=403, content=error_response.model_dump()
    #     )

    result = await admin_service.get_slider_detail(slider_id=path_params.id)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result 


@router.post("", response_model=SliderCreateResponse)
@log_event_detailed(action="CREATE", category=["ADMIN", "SLIDER_MANAGEMENT"])
async def create_slider(
    request: Request,
    # form_data: SliderCreateRequest = Depends(parse_slider_form_data),
    form_data: SliderCreateForm = Depends(),
    admin_service: SliderAdminService = Depends(get_admin_slider_service),
    image: Optional[UploadFile] = File(None)
):
    

    result = await admin_service.create_slider(
        request_data=form_data.model,
        image_file=image
    )

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)

    return result


@router.put("/{id}", response_model=SliderUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "SLIDER_MANAGEMENT"])
async def update_slider(
    request:Request,
    path_params: SliderPathParams = Depends(), 
    # form_data: SliderUpdateForm = Depends(),
    title: Optional[str] = Form(None),
    preview: Optional[str] = Form(None),
    tag: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    display_order: Optional[int] = Form(None),
    start_date: Optional[date] = Form(None),
    end_date: Optional[date] = Form(None),
    image: Optional[UploadFile] = File(None),
    # current_user: User = Depends(verify_active_user),
    admin_service: SliderAdminService = Depends(get_admin_slider_service)
):
    """
    기존 슬라이더의 정보를 수정
    - 텍스트 데이터와 함께 이미지를 새로 업로드하면 기존 이미지가 교체
    - 이미지를 업로드하지 않으면 기존 이미지는 그대로 유지
    """

    update_payload = {}

    # 각 필드를 확인하고, None이 아니고 Swagger UI의 기본값이 아닌 경우에만 추가
    if title is not None and title != "string":
        update_payload['title'] = title
    if preview is not None and preview != "string":
        update_payload['preview'] = preview
    if tag is not None and tag != "string":
        update_payload['tag'] = tag
    if content is not None and content != "string":
        update_payload['content'] = content
    
    if display_order is not None:
        update_payload['display_order'] = display_order
    if start_date is not None:
        update_payload['start_date'] = start_date
    if end_date is not None:
        update_payload['end_date'] = end_date

    request_data = SliderUpdateRequest(**update_payload)
    result = await admin_service.update_slider(
        slider_id = path_params.id,
        request_data=request_data,
        image_file=image
    )
    
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.UNAUTHORIZED:
            status_code = 401
        elif result.error.code == ErrorCode.FORBIDDEN:
            status_code = 403
        elif result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.FILE_TOO_LARGE:
            status_code = 413
        elif result.error.code == ErrorCode.VALIDATION_ERROR:
            status_code = 422
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result 


@router.patch("/{id}", response_model=SliderStatusUpdateResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "SLIDER_MANAGEMENT", "STATUS"])
async def update_slider_status (
    request:Request,
    payload: SliderStatusUpdateRequest,
    path_params: SliderPathParams = Depends(), 
    admin_service: SliderAdminService = Depends(get_admin_slider_service)
):

    result = await admin_service.update_slider_status(
        slider_id=path_params.id,
        is_active=payload.is_active
    )

    if isinstance(result, ErrorResponse):
        status_code_map = {
            ErrorCode.INTERNAL_ERROR: 500,
            ErrorCode.UNAUTHORIZED: 401,
            ErrorCode.FORBIDDEN: 403,
            ErrorCode.NOT_FOUND: 404,
            ErrorCode.FILE_TOO_LARGE: 413,
            ErrorCode.VALIDATION_ERROR: 422,
        }
        status_code = status_code_map.get(result.error.code, 500)
        return JSONResponse(status_code=status_code, content=result.model_dump())
    

    return result 

# 슬라이드 삭제
@router.delete("/{id}", response_model=SliderDeleteResponse)
@log_event_detailed(action="DELETE", category=["ADMIN", "SLIDER_MANAGEMENT"])
async def delete_slider(
    request:Request,
    path_params: SliderPathParams = Depends(), 
    # current_user: User = Depends(verify_active_user),
    admin_service: SliderAdminService = Depends(get_admin_slider_service)
):
    """특정 슬라이더를 데이터베이스에서 삭제하고, 연관된 이미지 파일도 함께 삭제"""
    result = await admin_service.delete_slider(path_params.id)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.UNAUTHORIZED:
            status_code = 401
        elif result.error.code == ErrorCode.FORBIDDEN:
            status_code = 403
        elif result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.FILE_TOO_LARGE:
            status_code = 413
        elif result.error.code == ErrorCode.VALIDATION_ERROR:
            status_code = 422
        return JSONResponse(status_code=status_code, content=result.model_dump())
    

    return result 
