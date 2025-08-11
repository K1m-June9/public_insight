from fastapi import APIRouter
from .auth import router as auth_router
from .test import router as test_router
from .slider import router as slider_router
from .static_page import router as static_page_router
from .organization import router as organization_router
from .feed import router as feed_router
from .users import router as users_router
from .notice import router as notice_router
from .search import router as search_router

from .admin import static_page as admin_static_page_router
from .admin import users as admin_users_router
from .admin import slider as admin_slider_router
from .admin import feed as admin_feed_router
from .admin import organization as admin_organization_router


# 메인 API 라우터 설정
router = APIRouter()

# /auth 엔드포인트 하위에 인증 라우터 연결
router.include_router(auth_router, prefix="/auth")

# /slider 엔드포인트 하위에 슬라이더 라우터 연결
router.include_router(slider_router, prefix="/sliders")

# /static-pages 엔드포인트 하위에 정적 페이지 라우터 연결
router.include_router(static_page_router, prefix="/static-pages")

# /organizations 엔드포인트 하위에 정적 페이지 라우터 연결
router.include_router(organization_router, prefix="/organizations")

# /feeds 엔드포인트 하위에 정적 페이지 라우터 연결
router.include_router(feed_router, prefix="/feeds")

# /users 엔드포인트 하위에 연결
router.include_router(users_router, prefix="/users")

# /notices 엔드포인트 하위에 연결
router.include_router(notice_router, prefix="/notices")

# /search 엔드포인트 하위에 연결
router.include_router(search_router, prefix="/search")

# admin API 그룹을 /admin prefix로 연결
#======================================================================
router.include_router(admin_static_page_router.router, prefix="/admin")
router.include_router(admin_feed_router.router, prefix="/admin")
router.include_router(admin_organization_router.router, prefix="/admin")
router.include_router(admin_users_router.router, prefix="/admin")
router.include_router(admin_slider_router.router, prefix="/admin")


#======================================================================
# 미들웨어와 verify_active_user 동작 테스트
router.include_router(test_router, prefix="/test")