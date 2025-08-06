import logging
from fastapi import APIRouter, Depends, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional

from app.F2_services.admin.feed import FeedAdminService
from app.F5_core.dependencies import get_admin_feed_service, verify_active_user
from app.F6_schemas.admin.feed import (
    OrganizationCategoriesResponse, 
    FeedListResponse, 
    FeedListRequest, 
    FeedDetailResponse, 
    FeedUpdateRequest, 
    FeedUpdateResponse, 
    ContentType, 
    FeedCreateRequest, 
    FeedCreateResponse,
    DeactivatedFeedListRequest,
    DeactivatedFeedListResponse,
    FeedDeleteResponse
    )
from app.F6_schemas.base import ErrorResponse, ErrorCode, PaginationQuery
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

@router.post("", response_model=FeedCreateResponse, status_code=202)
async def create_feed(
    tasks: BackgroundTasks,
    title: str = Form(...),
    organization_id: int = Form(...),
    category_id: int = Form(...),
    source_url: str = Form(...),
    published_date: str = Form(...),
    content_type: ContentType = Form(...),
    original_text: Optional[str] = Form(None),
    pdf_file: Optional[UploadFile] = File(None),
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 새로운 피드를 생성합니다. (비동기 처리)
    NLP 요약 등 시간이 오래 걸리는 작업은 백그라운드에서 처리
    """
    # 1. Form 데이터로 받은 값들을 Pydantic 스키마 객체로 변환
    request_data = FeedCreateRequest(
        title=title,
        organization_id=organization_id,
        category_id=category_id,
        source_url=source_url,
        published_date=published_date,
        content_type=content_type,
        original_text=original_text
    )

    # 2. 서비스 레이어 호출
    result = await admin_service.create_feed(
        request_data=request_data,
        pdf_file=pdf_file,
        tasks=tasks
    )

    if isinstance(result, ErrorResponse):
        # 비동기 처리 시작 전의 오류(예: DB 연결 실패)는 500 에러로 처리
        return JSONResponse(status_code=500, content=result.model_dump())

    # 성공 시, 서비스가 반환한 FeedCreateResponse 객체를 202 Accepted 상태 코드와 함께 반환
    return result

@router.get("/deactivated", response_model=DeactivatedFeedListResponse)
async def get_deactivated_feeds(
    query: DeactivatedFeedListRequest = Depends(),
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 비활성화된 피드 목록을 조회
    """
    result = await admin_service.get_deactivated_feeds_list(
        page=query.page,
        limit=query.limit
    )

    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    return result

@router.delete("/{id}", response_model=FeedDeleteResponse)
async def delete_feed(
    id: int,
    admin_service: FeedAdminService = Depends(get_admin_feed_service),
    current_user: User = Depends(verify_active_user)
):
    """
    관리자: 특정 피드를 데이터베이스에서 완전히 삭제
    """
    result = await admin_service.delete_feed_permanently(id)

    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result