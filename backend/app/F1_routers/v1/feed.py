from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
from app.F2_services.feed import FeedService
from app.F5_core.dependencies import get_feed_service, verify_active_user, verify_active_user_optional
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.feed import (
    MainFeedListResponse, 
    FeedListQuery, 
    OrganizationFeedListResponse, 
    OrganizationFeedQuery, 
    LatestFeedQuery, 
    LatestFeedResponse,
    OrganizationLatestFeedResponse,
    Top5FeedResponse,
    Top5FeedQuery,
    PressReleaseResponse,
    PressReleaseQuery,
    FeedDetailResponse,
    RatingRequest,
    RatingData,
    RatingResponse,
    BookmarkResponse,
    BookmarkData,
    BookmarkRequest
    )
from app.F6_schemas.recommendation import RecommendationResponse
from app.F6_schemas.base import PaginationQuery, ErrorResponse, ErrorCode
from app.F7_models.users import User

from app.F13_recommendations.dependencies import get_recommendation_service
from app.F13_recommendations.service import RecommendationService

logger = logging.getLogger(__name__)

# 피드 관련 API 라우터 생성
router = APIRouter()

# 메인 페이지 피드 목록 조회 엔드포인트
# HTTP 메서드: GET
# 경로: /api/feeds/
# 인증: 불필요
# 권한: 없음 (비로그인/로그인/관리자 상관없이 접근 가능)
# 목적: 메인 페이지 우측 피드 목록 조회
# 쿼리 파라미터:
#   - page: 페이지 번호 (기본값: 1, 최소값: 1)
#   - limit: 페이지당 항목 수 (기본값: 20, 최소값: 1, 최대값: 100)
# 응답: 피드 목록과 페이지네이션 정보를 포함한 JSON 응답 또는 에러 응답
@router.get("/", response_model=MainFeedListResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED"])
async def get_feeds(
    query: PaginationQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> MainFeedListResponse:
    """
    메인 페이지 피드 목록 조회
    
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    
    반환되는 데이터:
    - 피드 기본 정보 (제목, 요약, 발행일, 조회수)
    - 기관 정보 (ID, 이름)
    - 평균 별점
    - 페이지네이션 정보 (현재 페이지, 전체 페이지, 다음/이전 페이지 여부 등)
    
    에러 응답:
    - 500: 서버 내부 오류 발생 시
    """
    
    # PaginationQuery를 FeedListQuery로 변환
    # Service 레이어에서 요구하는 스키마 형태로 변환하여 전달
    feed_query = FeedListQuery(
        page=query.page,
        limit=query.limit
    )
    
    # 피드 서비스를 통해 메인 페이지 피드 목록 조회
    # Service 레이어에서 Repository 호출, 데이터 변환, 페이지네이션 처리 수행
    result = await feed_service.get_main_feed_list(feed_query)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 시 Service에서 반환된 MainFeedListResponse를 그대로 반환
    # FastAPI가 자동으로 JSON 직렬화 및 응답 스키마 검증 수행
    return result

@router.get("/top5", response_model=Top5FeedResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "TOP5"])
async def get_feeds_top5(
    query: Top5FeedQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> Top5FeedResponse:
    """
    메인 페이지 TOP5 피드 조회
    
    별점순, 조회수순, 북마크순 상위 피드를 각각 제공합니다.
    메인 페이지 좌측 TOP5 피드 게시 목록에서 사용됩니다.
    """
    # Service를 통해 TOP5 피드 데이터 조회
    result = await feed_service.get_top5_feeds(query.limit)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/latest", response_model=LatestFeedResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "LATEST"])
async def get_latest_feeds(
    query: LatestFeedQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> LatestFeedResponse:
    """
    메인 페이지 최신 피드 슬라이드 조회
    
    각 기관의 가장 최신 피드를 기관당 1개씩 제공합니다.
    메인 페이지 원형 그래프 아래 피드 슬라이드에서 사용됩니다.
    """
    # Service를 통해 최신 피드 데이터 조회
    result = await feed_service.get_latest_feeds_for_main(query.limit)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/detail/{id}", response_model=FeedDetailResponse)
@log_event_detailed(action="READ", category=["PUBLIC", "FEED", "DETAIL"])
async def get_feed_by_id(
    request:Request,
    id: int,
    feed_service: FeedService = Depends(get_feed_service),
    current_user: Optional[User] = Depends(verify_active_user_optional) #선택적 인증 메서드
) -> FeedDetailResponse:
    """
    피드 상세 정보 조회
    
    특정 피드의 상세 정보를 조회
    - 비로그인 사용자: 기본 정보만 제공
    - 로그인 사용자: 북마크 여부, 내가 매긴 별점 정보 추가 제공
    """
    user_pk = current_user.id if current_user else None # 인증된 사용자면 사용, 아니면 말고
    result = await feed_service.get_feed_detail_for_page(id, user_pk)
    
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        else:
            status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

# 별점 주기
@router.post("/detail/{id}/ratings", response_model=RatingResponse)
@log_event_detailed(action="CREATE", category=["USER", "FEED", "RATING"])
async def post_feed_rating(
    id: int, 
    payload: RatingRequest,
    feed_service: FeedService = Depends(get_feed_service),
    current_user: User = Depends(verify_active_user)
):
    result = await feed_service.post_feed_rating(id, current_user.user_id, payload.score)
    
    if isinstance(result, ErrorResponse):
        return JSONResponse(
            status_code=400, 
            content=result.model_dump())
    
    return result 


# 북마크
@router.post("/detail/{id}/bookmark", response_model=BookmarkResponse)
@log_event_detailed(action="CREATE", category=["USER", "FEED", "BOOKMARK"])
async def post_feed_bookmark(
    id: int, 
    payload: BookmarkRequest,
    feed_service: FeedService = Depends(get_feed_service),
    current_user: User = Depends(verify_active_user)
):
    result = await feed_service.post_feed_bookmark(id, current_user.user_id)

    if isinstance(result, ErrorResponse):
        return JSONResponse(
            status_code=400,
            content=result.model_dump()
        )
    return result

@router.get("/detail/{id}/recommendations", response_model=RecommendationResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "RECOMMENDATION"])
async def get_feed_recommendations(
    id: int,
    recommendation_service: RecommendationService = Depends(get_recommendation_service)
):
    """
    콘텐츠 기반 피드 추천 API
    
    특정 피드 ID를 기반으로, 함께 보기 좋은 유사 콘텐츠 목록을 반환함.
    - 현재 피드가 '정책 자료' -> 유사 정책 자료 + 관련 보도자료 추천
    - 현재 피드가 '보도자료' -> 유사 보도자료 + 관련 정책 자료 추천
    """
    result = await recommendation_service.get_recommendations_for_feed(id)
    
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result

# 기관별 피드 목록 조회 엔드포인트
# HTTP 메서드: GET
# 경로: /api/feeds/{name}
# 인증: 불필요
# 권한: 없음 (비로그인/로그인/관리자 상관없이 접근 가능)
# 목적: 기관 상세 페이지 우측 피드 목록 조회 (보도자료 제외)
# 경로 파라미터:
#   - name: 기관명 (한글 포함 가능)
# 쿼리 파라미터:
#   - page: 페이지 번호 (기본값: 1, 최소값: 1)
#   - limit: 페이지당 항목 수 (기본값: 20, 최소값: 1, 최대값: 100)
#   - category_id: 카테고리 ID (선택사항, 미입력시 전체 피드)
# 응답: 기관 정보, 피드 목록, 페이지네이션 정보, 필터 정보를 포함한 JSON 응답 또는 에러 응답
@router.get("/{name}", response_model=OrganizationFeedListResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "BY_ORGANIZATION"])
async def get_organization_feeds(
    name: str,
    query: OrganizationFeedQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> OrganizationFeedListResponse:
    """
    기관별 피드 목록 조회
    
    - **name**: 기관명 (예: 교육부, 고용노동부)
    - **page**: 페이지 번호 (1부터 시작)
    - **limit**: 페이지당 항목 수 (최대 100)
    - **category_id**: 카테고리 ID (선택사항, 특정 카테고리 필터링)
    
    반환되는 데이터:
    - 기관 정보 (ID, 이름)
    - 피드 목록 (제목, 카테고리, 요약, 발행일, 조회수, 평균 별점)
    - 페이지네이션 정보 (현재 페이지, 전체 페이지, 다음/이전 페이지 여부 등)
    - 필터 정보 (카테고리 필터링 적용 시)
    
    에러 응답:
    - 404: 존재하지 않는 기관명인 경우
    - 500: 서버 내부 오류 발생 시
    
    주의사항:
    - '보도자료' 카테고리는 자동으로 제외됩니다
    """
    
    # 피드 서비스를 통해 기관별 피드 목록 조회
    # Service 레이어에서 Repository 호출, 데이터 변환, 페이지네이션 처리 수행
    # 기관명과 쿼리 파라미터(페이지네이션, 카테고리 필터)를 함께 전달
    result = await feed_service.get_organization_feed_list(name, query)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        # 에러 코드에 따라 HTTP 상태 코드 설정
        # ORGANIZATION_NOT_FOUND: 404, INTERNAL_SERVER_ERROR: 500
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 시 Service에서 반환된 OrganizationFeedListResponse를 그대로 반환
    # FastAPI가 자동으로 JSON 직렬화 및 응답 스키마 검증 수행
    return result

@router.get("/{name}/latest", response_model=OrganizationLatestFeedResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "BY_ORGANIZATION", "LATEST"])
async def get_organization_feeds_latest(
    name: str,
    query: LatestFeedQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> OrganizationLatestFeedResponse:
    """
    기관 페이지 최신 피드 슬라이드 조회
    
    해당 기관의 각 카테고리별 최신 피드를 카테고리당 1개씩 제공
    기관 페이지 원형 그래프 아래 피드 슬라이드에서 사용
    """
    # Service를 통해 기관별 카테고리별 최신 피드 데이터 조회
    result = await feed_service.get_organization_latest_feeds(name, query.limit)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/{name}/press", response_model=PressReleaseResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "FEED", "BY_ORGANIZATION", "PRESS"])
async def get_press_releases(
    name: str,
    query: PressReleaseQuery = Depends(),
    feed_service: FeedService = Depends(get_feed_service)
) -> PressReleaseResponse:
    """
    기관 페이지 보도자료 목록 조회
    
    각 기관의 보도자료 목록을 페이지네이션과 함께 제공
    기관 페이지 좌측 하단 보도자료 리스트에서 사용
    """
    # Service를 통해 기관별 보도자료 데이터 조회
    result = await feed_service.get_organization_press_releases(name, query)
    
    # Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        elif result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        else:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

