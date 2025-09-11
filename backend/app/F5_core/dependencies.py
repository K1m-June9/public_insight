from fastapi import Depends, Request, HTTPException, status
from elasticsearch import AsyncElasticsearch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.F5_core.config import settings

from app.F2_services.auth import AuthService
from app.F2_services.slider import SliderService
from app.F2_services.session import SessionService
from app.F2_services.static_page import StaticPageService
from app.F2_services.organization import OrganizationService
from app.F2_services.feed import FeedService
from app.F2_services.users import UserService
from app.F2_services.notice import NoticeService

from app.F2_services.admin.static_page import StaticPageAdminService
from app.F2_services.admin.users import UsersAdminService
from app.F2_services.admin.slider import SliderAdminService
# from app.F2_services.admin.feed import FeedAdminService
from app.F2_services.admin.organization import OrganizationAdminService
from app.F2_services.admin.notices import NoticesAdminService
from app.F2_services.admin.dashboard import DashboardAdminService

from app.F3_repositories.auth import AuthRepository
from app.F3_repositories.slider import SliderRepository
from app.F3_repositories.session import SessionRepository
from app.F3_repositories.organization import OrganizationRepository
from app.F3_repositories.feed import FeedRepository
from app.F3_repositories.users import UserRepository
from app.F3_repositories.static_page import StaticPageRepository
from app.F3_repositories.notice import NoticeRepository


from app.F3_repositories.admin.static_page import StaticPageAdminRepository
from app.F3_repositories.admin.users import UsersAdminRepository
from app.F3_repositories.admin.activity_log import UsersActivityRepository
from app.F3_repositories.admin.slider import SliderAdminRepository
# from app.F3_repositories.admin.feed import FeedAdminRepository
from app.F3_repositories.admin.organization import OrganizationAdminRepository
from app.F3_repositories.admin.notices import NoticesAdminRepository
from app.F3_repositories.admin.dashboard import DashboardAdminRepository
from app.F3_repositories.admin.dashboard_activity import DashboardActivityRepository

from app.F4_utils.email import EmailVerificationService
from app.F5_core.redis import RedisCacheService, PasswordResetRedisService
from app.F5_core.security import AuthHandler
from app.F6_schemas.base import UserRole
from app.F7_models.users import UserStatus, User
from app.F8_database.session import get_db
from app.F11_search.ES1_client import es_async
from app.F8_database.graph_db import Neo4jDriver # 👈 Neo4jDriver를 직접 import
from neo4j import AsyncSession

#------------------------------------------------
# PoC
#------------------------------------------------
from app.F2_services.graph import GraphService
from app.F3_repositories.graph import GraphRepository
#------------------------------------------------
def get_graph_repository(session: AsyncSession = Depends(Neo4jDriver.get_driver)) -> GraphRepository:
    """그래프 DB 리포지토리 의존성 주입용 함수"""
    return GraphRepository(session)

def get_graph_service(repo: GraphRepository = Depends(get_graph_repository)) -> GraphService:
    """그래프 DB 서비스 의존성 주입용 함수"""
    return GraphService(repo)
#------------------------------------------------

# --- 일반 ---
def get_es_client() -> AsyncElasticsearch:
    """ES 클라이언트를 반환하는 의존성 함수"""
    return es_async

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """인증 의존성 주입용 함수"""
    return AuthService(AuthRepository(db))

async def get_slider_service(db: AsyncSession = Depends(get_db)) -> SliderService:
    """슬라이더 서비스 의존성 주입용 함수"""
    return SliderService(SliderRepository(db))

async def get_static_page_service(db: AsyncSession = Depends(get_db)) -> StaticPageService:
    """정적 페이지 서비스 의존성 주입용 함수"""
    return StaticPageService(StaticPageRepository(db))

def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """세션 주입용 함수"""
    return SessionService(SessionRepository(db))

def get_password_reset_redis_service() -> PasswordResetRedisService:
    """비밀번호 재설정용 Redis 서비스 의존성 주입 함수"""
    return PasswordResetRedisService()

async def get_email_verification_services() -> EmailVerificationService:
    """이메일 인증 의존성 주입용 함수"""
    return EmailVerificationService()

async def get_organization_service(db: AsyncSession = Depends(get_db)) -> OrganizationService:
    """기관/카테고리 관련 서비스 의존성 주입용 함수"""
    return OrganizationService(OrganizationRepository(db))

async def get_feed_service(db: AsyncSession = Depends(get_db)) -> FeedService:
    """피드 관련 서비스 의존성 주입용 함수"""
    return FeedService(FeedRepository(db))

async def get_user_service(
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service)
    ) -> UserService:
    """사용자 관련 서비스 의존성 주입용 함수"""
    
    user_repo = UserRepository(db)

async def get_user_service(db: AsyncSession = Depends(get_db),session_service: SessionService = Depends(get_session_service)) -> UserService:
    """사용자 관련 서비스 의존성 주입용 함수"""    
    user_repo = UserRepository(db)
    return UserService(repo=user_repo, session_service=session_service)

async def get_notice_service(db: AsyncSession = Depends(get_db)) -> NoticeService:
    return NoticeService(NoticeRepository(db))

async def get_auth_handler() -> AuthHandler:
    return AuthHandler()


# --- 관리자 ---
async def get_admin_static_page_service(db: AsyncSession = Depends(get_db)) -> StaticPageAdminService:
    """관리자 정적 페이지 관련 의존성 주입용 함수"""
    return StaticPageAdminService(StaticPageAdminRepository(db))

async def get_admin_slider_service(db: AsyncSession = Depends(get_db)) -> SliderAdminService:
    return SliderAdminService(SliderAdminRepository(db))

async def get_admin_users_service(
    db: AsyncSession = Depends(get_db),
    es: AsyncElasticsearch = Depends(get_es_client)
) -> UsersAdminService:
    """관리자 유저(관리) 관련 의존성 주입용 함수"""
    user_repo = UsersAdminRepository(db=db)
    activity_repo = UsersActivityRepository(es=es)
    return UsersAdminService(user_repo=user_repo, activity_repo=activity_repo)

# async def get_admin_feed_service(db: AsyncSession = Depends(get_db)) -> FeedAdminService:
#     """관리자 피드 관련 의존성 주입용 함수"""
#     return FeedAdminService(FeedAdminRepository(db))

async def get_admin_organization_service(db: AsyncSession = Depends(get_db)) -> OrganizationAdminService:
    """관리자 기관/카테고리 관련 의존성 주입용 함수"""
    return OrganizationAdminService(OrganizationAdminRepository(db))

async def get_admin_notices_service(db: AsyncSession=Depends(get_db)) -> NoticesAdminService:
    """관리자 공지사항 관련 의존성 주입용 함수"""
    return NoticesAdminService(NoticesAdminRepository(db))


async def get_admin_dashboard_service(
        #db: AsyncSession=Depends(get_db),
        es: AsyncElasticsearch = Depends(get_es_client)
) -> DashboardAdminService:
    """관리자 대시보드 관련 의존성 주입용 함수"""
    dash_repo = DashboardAdminRepository()
    es_repo = DashboardActivityRepository(es=es)
    return DashboardAdminService(dash_repo=dash_repo, es_repo=es_repo)





# async def verify_active_user(
#     request: Request,
#     db: AsyncSession = Depends(get_db),
# ) -> User:
#     """요청에 인증된 사용자가 활성 상태인지 검증하는 함수(Redis 캐시 사용)"""
    
#     user_id = getattr(request.state, "user_id", None)
#     if not user_id:
#         # user_id가 없으면 안 된 상태
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

#     # 1. Redis 캐시 조회 시도
#     cached = await RedisCacheService.get_cached_user_info(user_id)

#     if cached:
#         required_fields = ("user_id", "nickname", "email", "status", "role")
#         if not all(field in cached and cached[field] is not None for field in required_fields):
#             cached = None

#     if cached:
#         # 캐시가 존재하면 상태만 검사
#         if cached.get("status") != UserStatus.ACTIVE.value:
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")
    
    
#     # 2. 캐시가 없으면 DB 조회
#     auth_repo = AuthRepository(db)
#     user = await auth_repo.get_user_by_user_id(user_id)
#     if not user:
#         # DB에 해당 사용자 없음
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     if user.status != UserStatus.ACTIVE:
#         # 사용자 상태가 활성 상태가 아님(예: 차단, 비활성)
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")

#     # 3. DB 조회 후 Redis 캐시에 저장
#     await RedisCacheService.cache_user_info(user)

#     return user



#####################################################
# swaggerUI를 위해 수정된 상태
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def verify_active_user(
    request: Request,
    # 수정된 부분
    token: str = Depends(oauth2_scheme),
    
    db: AsyncSession = Depends(get_db),
) -> User:
    """요청에 인증된 사용자가 활성 상태인지 검증하고, request.state에 사용자 정보를 저장합니다."""
    # JWT 미들웨어에서 user_id를 전달받았다고 가정합니다.
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}, # 401 응답 표준 헤더 추가
        )

    # 1. Redis 캐시 조회 시도
    cached = await RedisCacheService.get_cached_user_info(user_id)

    # 캐시 데이터 유효성 검사 (선택사항이지만 좋은 습관)
    if cached:
        required_fields = ("user_id", "nickname", "email", "status", "role")
        if not all(field in cached and cached[field] is not None for field in required_fields):
            cached = None

    if cached:
        # 캐시가 존재하면 상태만 검사
        if cached.get("status") != UserStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")
        
        # 캐시된 데이터로 User 객체를 생성하여 일관성을 유지
        user = User(
            user_id=cached.get("user_id"),
            nickname=cached.get("nickname"),
            email=cached.get("email"),
            status=UserStatus(cached.get("status")),
            role=UserRole(cached.get("role"))
        )
        
        # request.state에 저장하고 반환
        request.state.user = user
        return user
    
    # 2. 캐시가 없으면 DB 조회
    auth_repo = AuthRepository(db)
    user = await auth_repo.get_user_by_user_id(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")

    # 3. DB 조회 후 Redis 캐시에 저장
    await RedisCacheService.cache_user_info(user)

    # request.state에 저장하고 반환
    request.state.user = user
    return user


#   새로운 선택적 인증 함수 추가
#   로직 자체는 verify_active_user와 동일
#   사용자가 없으면 None 반환 -> 선택적 인증(None이면 인증 X)
async def verify_active_user_optional(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    요청에 유효한 토큰이 있는 경우에만 사용자 정보를 반환하고,
    그렇지 않은 경우 None을 반환하는 선택적 인증 함수.
    """
    
    # JWT 미들웨어가 에러를 발생시키지 않고, request.state에 user_id를 설정했다면
    # (즉, 유효한 토큰이 헤더에 있었다면) user_id를 가져옴
    user_id = getattr(request.state, "user_id", None)
    
    # 토큰이 없었으면 user_id는 None이므로, 그대로 None을 반환
    if not user_id:
        return None

    # 토큰이 있었다면, 기존 verify_active_user와 동일한 검증 로직 수행
    # 단, 오류 발생 시 HTTPException 대신 None을 반환하여 API 실행이 중단되지 않도록 함
    try:
        # Redis 캐시 확인 등 기존 로직 재사용
        cached = await RedisCacheService.get_cached_user_info(user_id)
        if cached and cached.get("status") != UserStatus.ACTIVE.value:
            return None # 비활성 사용자는 로그인하지 않은 것과 동일하게 취급

        auth_repo = AuthRepository(db)
        user = await auth_repo.get_user_by_user_id(user_id)

        if not user or user.status != UserStatus.ACTIVE:
            return None

        # 캐시가 없었다면 저장
        if not cached:
            await RedisCacheService.cache_user_info(user)
            
        return user
    except Exception:
        # 검증 과정에서 어떤 예외가 발생하더라도 None을 반환
        return None
    