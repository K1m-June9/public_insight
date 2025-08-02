import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.F2_services.admin.static_page import StaticPageAdminService
from app.F5_core.dependencies import get_admin_static_page_service, verify_active_user # 💡 verify_active_user 임포트
from app.F6_schemas.admin.static_page import StaticPageListResponse
from app.F6_schemas.base import ErrorResponse
from app.F7_models.users import User # 💡 User 모델 임포트

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Admin-StaticPages"],
    prefix="/static-pages"
)

@router.get("", response_model=StaticPageListResponse)
async def get_static_pages(
    admin_service: StaticPageAdminService = Depends(get_admin_static_page_service),
    # 💡 우선은 '활성 사용자'인지 확인하는 것으로 인증을 처리
    # 추후 'ADMIN' 역할을 확인하는 의존성(verify_admin_user)으로 교체하는 것이 좋음
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 모든 정적 페이지 목록을 조회
    """
    # 1. 서비스 레이어를 호출하여 결과를 받음
    result = await admin_service.get_static_pages_list()

    # 2. 결과가 ErrorResponse 객체이면, 에러 응답을 반환
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    # 3. 성공 시, 성공 응답 객체를 반환
    return result