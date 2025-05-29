from fastapi import APIRouter

# 커스텀 모듈
from app.routers.users.check_router import router as check_router
from app.routers.users.email_router import router as email_router
from app.routers.users.signup_router import router as signup_router

from app.routers.oauth2.log_router import router as log_router
api_router = APIRouter()

# 각 API 엔드포인트를 라우터에 등록
api_router.include_router(check_router, prefix="/users")
api_router.include_router(email_router, prefix="/users")
api_router.include_router(signup_router, prefix="/users")

api_router.include_router(log_router, prefix="/auth")