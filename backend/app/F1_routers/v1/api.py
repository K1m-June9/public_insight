from fastapi import APIRouter
from .auth import router as auth_router
from .test import router as test_router
from .slider import router as slider_router
from .static_page import router as static_page_router
from .organization import router as organization_router
from .feed import router as feed_router

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

# 미들웨어와 verify_active_user 동작 테스트
router.include_router(test_router, prefix="/test")