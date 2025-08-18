import logging
import json 

from fastapi import APIRouter, Depends, Request, Form, File, UploadFile, Body, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, Dict, Any
from datetime import date
from pydantic import ValidationError

from app.F2_services.admin.dashboard import DashboardAdminService
from app.F5_core.config import settings
from app.F5_core.dependencies import verify_active_user, get_admin_dashboard_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.base import ErrorResponse, ErrorCode, PaginationQuery

from app.F7_models.users import User
from app.F7_models.feeds import Feed
from app.F7_models.organizations import Organization
from app.F7_models.sliders import Slider
from app.F7_models.notices import Notice
from app.F7_models.bookmarks import Bookmark
from app.F7_models.ratings import Rating

# --- 로그 관련 테이블 ➡️ 엘라스틱 서치로 대체 ---
from app.F7_models.search_logs import SearchLog
from app.F7_models.user_activities import UserActivity

from app.F6_schemas.admin.dashboard import(
    DashboardResponse,
)



logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin-Dashboard"], prefix="/dashboard")

def handle_error_response(result: ErrorResponse) -> JSONResponse:
    """
    서비스 레이어로부터 받은 ErrorResponse 객체를 적절한 HTTP 상태코드와 함께 JSONResponse로 변환
    """
    status_code_map = {
        ErrorCode.UNAUTHORIZED: 401,
        ErrorCode.FORBIDDEN: 403,
        ErrorCode.NOT_FOUND: 404,
        ErrorCode.INTERNAL_ERROR: 500,
    }
    status_code = status_code_map.get(result.error.code, 500)

    return JSONResponse(
        status_code=status_code,
        content=result.model_dump()
    )


@router.get("", response_model=DashboardResponse)
@log_event_detailed(action="READ", category=["ADMIN", "DASHBOARD"])
async def get_dashboard_stats(
    request:Request,
    current_user: User = Depends(verify_active_user),
    admin_service: DashboardAdminService = Depends(get_admin_dashboard_service),
):
    result = await admin_service.get_dashboard_stats(current_user)

    if isinstance(result, ErrorResponse):
        return handle_error_response(result)
    
    return result