import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.F2_services.admin.users import UsersAdminService
from app.F5_core.dependencies import verify_active_user, get_admin_users_service
from app.F6_schemas.base import ErrorResponse, ErrorCode, PaginationQuery
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.admin.users import (
    UserListResponse,
    UserListRequest,
    UserRole,
    UserDetailResponse,
    UserActivityResponse,
    UserRoleChangeResponse,
    UserRoleChangeRequest,
    UserStatusChangeResponse,
    UserStatusChangeRequest,



    )
from app.F7_models.users import User 

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin-Users"], prefix="/users")

@router.get("",response_model=UserListResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "USER_MANAGEMENT"])
async def get_user_list(
    request: Request,
    # current_user: User = Depends(verify_active_user),
    admin_service: UsersAdminService = Depends(get_admin_users_service),
    params: UserListRequest = Depends()
):
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

    result = await admin_service.get_user_list(params)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())

    return result

@router.get("/{id}",response_model=UserDetailResponse)
@log_event_detailed(action="READ", category=["ADMIN", "USER_MANAGEMENT", "DETAIL"])
async def get_user_detail(
    request: Request,
    id : str,
    # current_user: User = Depends(verify_active_user),
    admin_service: UsersAdminService = Depends(get_admin_users_service),
):
    """특정 사용자의 상세 정보와 개인 활동 통계를 조회"""
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

    user_id = id 
    result = await admin_service.get_user_detail(user_id)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result


@router.get("/{id}/activities",response_model=UserActivityResponse)
@log_event_detailed(action="LIST", category=["ADMIN", "USER_MANAGEMENT", "ACTIVITY_LOG"])
async def get_user_detail_log(
    request:Request,
    id: str,
    # current_user: User = Depends(verify_active_user),
    admin_service: UsersAdminService = Depends(get_admin_users_service),
    pagination: PaginationQuery = Depends()
):
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
    user_id = id
    result = await admin_service.get_user_detail_log(user_id, pagination.page, pagination.limit)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result


@router.patch("/{id}/role", response_model=UserRoleChangeResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "USER_MANAGEMENT", "ROLE"])
async def update_user_role(
    request:Request,
    request_body:UserRoleChangeRequest,
    id: str,
    # current_user: User = Depends(verify_active_user),
    admin_service: UsersAdminService = Depends(get_admin_users_service),
):
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
    user_id = id 
    
    result = await admin_service.update_user_role(user_id= user_id, new_role=request_body.role)
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.FORBIDDEN:
            status_code=403
        elif result.error.code == ErrorCode.INVALID_PARAMETER:
            status_code=400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result



@router.patch("/{id}/status", response_model=UserStatusChangeResponse)
@log_event_detailed(action="UPDATE", category=["ADMIN", "USER_MANAGEMENT", "STATUS"])
async def update_user_role(
    request:Request,
    request_body:UserStatusChangeRequest,
    id: str,
    # current_user: User = Depends(verify_active_user),
    admin_service: UsersAdminService = Depends(get_admin_users_service),
):
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
    user_id = id 

    result = await admin_service.update_user_status(user_id=user_id, new_status=request_body.status)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.FORBIDDEN:
            status_code=403
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result
    