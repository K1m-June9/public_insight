import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.F1_routers.v1.api import router as api_v1_router
from app.F7_models import (
    bookmarks, categories, feeds, keywords, notices, organizations, rating_history, ratings, refresh_token, search_logs, sliders, static_page_versions, static_pages, token_security_event_logs, user_activities, user_interests, users, word_clouds
    )
from app.F8_database.connection import engine, Base 
from app.F9_middlewares.jwt_bearer_middleware import JWTBearerMiddleware
from app.F9_middlewares.admin_paths import admin_paths
from app.F9_middlewares.exempt_paths import exempt_paths, exempt_regex_paths
from app.F5_core.config import settings 

# 환경 변수 로드
load_dotenv()
if not settings.JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY 환경 변수가 설정되지 않았습니다.")

# 앱 라이프사이클 컨텍스트 매니저: 시작 시 DB 테이블 생성
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 종료 시 추가 로직 필요하면 작성

# FastAPI 앱 초기화
app = FastAPI(
    lifespan=app_lifespan,
    docs_url="/docs",
    redoc_url=None,
    title="MyProject API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 운영 시 도메인 제한 권장
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 세션 미들웨어
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)

# static 폴더 절대 경로
STATIC_DIR = Path(__file__).resolve().parent / "static"

# 정적 파일 전달(현재는 PDF)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# JWT 인증 미들웨어
app.add_middleware(
    JWTBearerMiddleware,
    exempt_paths=exempt_paths,
    exempt_regex_paths=exempt_regex_paths,
    admin_paths=admin_paths
)

# 라우터 등록
app.include_router(api_v1_router, prefix="/api/v1")

"""
앱 종료시 같이 redis 닫아주기
@app.on_event("shutdown")
async def shutdown_event():
    await client_redis.close()
    await email_redis.close()
    await token_redis.close()

"""