from fastapi import APIRouter
from .auth import router as auth_router
from .test import router as test_router

# 메인 API 라우터 설정
router = APIRouter()

# /auth 엔드포인트 하위에 인증 라우터 연결
router.include_router(auth_router, prefix="/auth")

# 미들웨어와 verify_active_user 동작 테스트
router.include_router(test_router, prefix="/test")