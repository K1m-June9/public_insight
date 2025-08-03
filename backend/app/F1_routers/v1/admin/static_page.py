import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.F2_services.admin.static_page import StaticPageAdminService
from app.F5_core.dependencies import get_admin_static_page_service, verify_active_user 
from app.F6_schemas.admin.static_page import StaticPageListResponse, StaticPageUpdateResponse, StaticPageDetailResponse, StaticPageUpdateRequest
from app.F6_schemas.base import ErrorResponse, ErrorCode
from app.F7_models.users import User 

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Admin-StaticPages"],
    prefix="/static-pages" #이게 이런 방법이 최선인지는 조금 더 확인해봐야 할 것 같음.
)

@router.get("", response_model=StaticPageListResponse)
async def get_static_pages(
    admin_service: StaticPageAdminService = Depends(get_admin_static_page_service),
    # 우선은 '활성 사용자'인지 확인하는 것으로 인증을 처리
    # 추후 'ADMIN' 역할을 확인하는 의존성(verify_admin_user)으로 교체할수도 있음
    # 근데 middleware에서 admin_paths 사용중이어서 크게 상관 없을 것 같기도 함
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

@router.get("/{slug}", response_model=StaticPageDetailResponse)
async def get_static_page_detail(
    slug: str,
    admin_service: StaticPageAdminService = Depends(get_admin_static_page_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: slug로 특정 정적 페이지의 상세 정보를 조회
    """
    result = await admin_service.get_static_page_detail(slug)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.put("/{slug}", response_model=StaticPageUpdateResponse)
async def update_static_page(
    slug: str,
    request: StaticPageUpdateRequest,
    admin_service: StaticPageAdminService = Depends(get_admin_static_page_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 정적 페이지의 내용을 수정
    """
    result = await admin_service.update_static_page(slug, request.content)

    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.BAD_REQUEST:
            status_code = 400
        else:
            status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result