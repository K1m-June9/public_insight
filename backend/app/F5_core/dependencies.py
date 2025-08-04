from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.F2_services.auth import AuthService
from app.F2_services.slider import SliderService
from app.F2_services.session import SessionService
from app.F2_services.static_page import StaticPageService
from app.F2_services.organization import OrganizationService
from app.F2_services.feed import FeedService
from app.F2_services.users import UserService
from app.F2_services.notice import NoticeService

from app.F2_services.admin.static_page import StaticPageAdminService

from app.F3_repositories.auth import AuthRepository
from app.F3_repositories.slider import SliderRepository
from app.F3_repositories.session import SessionRepository
from app.F3_repositories.organization import OrganizationRepository
from app.F3_repositories.feed import FeedRepository
from app.F3_repositories.users import UserRepository
from app.F3_repositories.static_page import StaticPageRepository
from app.F3_repositories.notice import NoticeRepository

from app.F3_repositories.admin.static_page import StaticPageAdminRepository

from app.F4_utils.email import EmailVerificationService
from app.F5_core.redis import RedisCacheService, PasswordResetRedisService
from app.F5_core.security import AuthHandler
from app.F7_models.users import UserStatus, User
from app.F8_database.session import get_db


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

async def get_admin_static_page_service(db: AsyncSession = Depends(get_db)) -> StaticPageAdminService:
    """관리자 정적 페이지 관련 의존성 주입용 함수"""
    return StaticPageAdminService(StaticPageAdminRepository(db))

async def get_user_service(
    db: AsyncSession = Depends(get_db),
    session_service: SessionService = Depends(get_session_service)
    ) -> UserService:
    """사용자 관련 서비스 의존성 주입용 함수"""
    
    user_repo = UserRepository(db)

    return UserService(repo=user_repo, session_service=session_service)

async def get_notice_service(db: AsyncSession = Depends(get_db)) -> NoticeService:
    return NoticeService(NoticeRepository(db))

async def get_auth_handler() -> AuthHandler:
    return AuthHandler()



async def verify_active_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """요청에 인증된 사용자가 활성 상태인지 검증하는 함수(Redis 캐시 사용)"""
    
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # user_id가 없으면 안 된 상태
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # 1. Redis 캐시 조회 시도
    cached = await RedisCacheService.get_cached_user_info(user_id)

    if cached:
        required_fields = ("user_id", "nickname", "email", "status", "role")
        if not all(field in cached and cached[field] is not None for field in required_fields):
            cached = None

    if cached:
        # 캐시가 존재하면 상태만 검사
        if cached.get("status") != UserStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")
    
    
    # 2. 캐시가 없으면 DB 조회
    auth_repo = AuthRepository(db)
    user = await auth_repo.get_user_by_user_id(user_id)
    if not user:
        # DB에 해당 사용자 없음
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.status != UserStatus.ACTIVE:
        # 사용자 상태가 활성 상태가 아님(예: 차단, 비활성)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")

    # 3. DB 조회 후 Redis 캐시에 저장
    await RedisCacheService.cache_user_info(user)

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
    