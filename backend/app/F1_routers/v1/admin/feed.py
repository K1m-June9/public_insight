import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.F2_services.admin.feed import FeedAdminService
from app.F5_core.dependencies import get_admin_feed_service, verify_active_user
from app.F6_schemas.admin.feed import OrganizationCategoriesResponse, FeedListResponse, FeedListRequest, FeedDetailResponse, FeedUpdateRequest, FeedUpdateResponse
from app.F6_schemas.base import ErrorResponse, ErrorCode
from app.F7_models.users import User

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Admin-Feeds"],
    prefix="/feeds"
)

@router.get("", response_model=FeedListResponse)
async def get_feeds_list(
    query: FeedListRequest = Depends(),
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 피드 목록을 페이지네이션, 검색, 필터링하여 조회
    """
    result = await admin_service.get_feeds_list(
        page=query.page,
        limit=query.limit,
        search=query.search,
        organization_id=query.organization_id,
        category_id=query.category_id
    )

    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    return result

@router.get("/organizations/{organization_id}/categories", response_model=OrganizationCategoriesResponse)
async def get_organization_categories(
    organization_id: int,
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 기관에 속한 카테고리 목록을 조회
    (피드 생성/수정 시 드롭다운 메뉴를 채우기 위해 사용)
    """
    result = await admin_service.get_organization_categories(organization_id)

    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    return result

@router.get("/{id}", response_model=FeedDetailResponse)
async def get_feed_detail(
    id: int,
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: ID로 특정 피드의 상세 정보를 조회
    """
    result = await admin_service.get_feed_detail(id)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.put("/{id}", response_model=FeedUpdateResponse)
async def update_feed(
    id: int,
    request: FeedUpdateRequest,
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 피드의 정보를 수정 (NLP 재처리 없음)
    """
    result = await admin_service.update_feed(id, request)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result