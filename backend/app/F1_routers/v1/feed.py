from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import logging
from app.F2_services.feed import FeedService
from app.F5_core.dependencies import get_feed_service
from app.F6_schemas.feed import MainFeedListResponse, FeedListQuery, OrganizationFeedListResponse, OrganizationFeedQuery
from app.F6_schemas.base import PaginationQuery, ErrorResponse

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
        # INTERNAL_SERVER_ERROR의 경우 500 상태 코드로 응답
        status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 시 Service에서 반환된 MainFeedListResponse를 그대로 반환
    # FastAPI가 자동으로 JSON 직렬화 및 응답 스키마 검증 수행
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
        status_code = 404 if result.error.code == "ORGANIZATION_NOT_FOUND" else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 시 Service에서 반환된 OrganizationFeedListResponse를 그대로 반환
    # FastAPI가 자동으로 JSON 직렬화 및 응답 스키마 검증 수행
    return result