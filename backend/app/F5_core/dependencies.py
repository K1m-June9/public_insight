from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.F2_services.auth import AuthService
from app.F2_services.slider import SliderService
from app.F3_repositories.auth import AuthRepository
from app.F3_repositories.slider import SliderRepository
from app.F5_core.redis import RedisCacheService
from app.F8_database.session import get_db
from app.F7_models.users import User, UserStatus



async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """의존성 주입용 함수"""
    return AuthService(AuthRepository(db))

async def get_slider_service(db: AsyncSession = Depends(get_db)) -> SliderService:
    """슬라이더 서비스 의존성 주입용 함수"""
    return SliderService(SliderRepository(db))

async def verify_active_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """요청에 인증된 사용자가 활성 상태인지 검증하는 함수(Redis 캐시 사용)"""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        # user_id가 없으면 안 된 상태
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # 1. Redis 캐시 조회 시도
    cached = await RedisCacheService.get_cached_user_info(user_id)

    if cached:
        # 캐시가 존재하면 상태만 검사
        if cached.get("status") != UserStatus.ACTIVE.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or blocked")
        
        return cached
    
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