import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import logging
import ecs_logging 
import uvicorn 

# --- 설정 및 초기화 관련 모듈을 먼저 import ---
from app.F5_core.config import settings 
from app.F11_search.es_initializer import initialize_elasticsearch
from app.F8_database.connection import engine, Base 

# --- 라우터 및 미들웨어 관련 모듈 import ---
from app.F1_routers.v1.api import router as api_v1_router
from app.F9_middlewares.logging_middleware import LoggingMiddleware
from app.F9_middlewares.jwt_bearer_middleware import JWTBearerMiddleware
from app.F9_middlewares.admin_paths import admin_paths, admin_regex_paths
from app.F9_middlewares.exempt_paths import exempt_paths, exempt_regex_paths

# --- 모델 import (Base.metadata.create_all을 위해 필요) ---
from app.F7_models import (
    bookmarks, categories, feeds, keywords, notices, organizations, rating_history, ratings, refresh_token, search_logs, sliders, static_page_versions, static_pages, token_security_event_logs, user_activities, user_interests, users, word_clouds
    )


# ==================================
# 1. 로깅 설정 함수
# ==================================
def configure_logging():
    """애플리케이션의 모든 로거를 설정"""

    # 기존 로거 핸들러 제거 (중복 출력 방지)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # 핸들러 및 포맷터 설정
    handler = logging.StreamHandler()

    # 환경에 따라 포맷터를 다르게 설정
    if settings.ENVIRONMENT == 'production':
        # 운영환경: ECS JSON 포맷터(분석 및 중앙화 로그 수집용)
        formatter = ecs_logging.StdlibFormatter()
        # 운영환경에서는 Uvicorn 로거가 INFO를 찍도로 설정
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.setLevel(logging.INFO)

    else:
        # 개발환경: 사람이 읽기 좋은 텍스트 포맷터(터미널에서 디버깅용)
        formatter = logging.Formatter(
            "%(levelname)s: [%(name)s] %(message)s"
        )
        # 개발환경에서는 Uvicorn 로거가 DEBUG를 찍도록 설정
        uvicorn_logger = logging.getLogger("uvicorn")
        uvicorn_logger.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)

    # .env 파일의 LOG_LEVEL을 동적으로 적용
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


# ==================================
# 2. 애플리케이션 라이프사이클 관리
# ==================================

# 앱 라이프사이클 컨텍스트 매니저: 시작 시 DB 테이블 생성
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """애플리케이션 시작 및 종료 시 실행될 로직을 관리"""
    logger = logging.getLogger(__name__)
    logger.info("Application startup sequence initiated...")

    # DB 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables checked/created.")


    # Elasticsearch 초기화 함수 호출
    initialize_elasticsearch()
    
    yield
    # 종료 시 추가 로직 필요하면 작성

    logger.info("Application shutdown sequence initiated.")
    # 앱 종료 시 redis 연결 종료 등 추가 로직
    # await client_redis.close()
    # await email_redis.close()
    # await token_redis.close()


"""
앱 종료시 같이 redis 닫아주기
@app.on_event("shutdown")
async def shutdown_event():
    await client_redis.close()
    await email_redis.close()
    await token_redis.close()

"""

# ==================================
# 3. 애플리케이션 팩토리 함수
# ==================================
def create_app() -> FastAPI:
    """FastAPI 앱 인스턴스를 생성하고 설정하여 반환"""

    # 로깅 설정 함수 호출
    configure_logging()

    # 생성되는 모든 로그는 위에서 설정한 포맷을 따름
    logger = logging.getLogger(__name__)

    # 환경 변수 검증
    if not settings.JWT_SECRET_KEY:
        logger.critical("JWT_SECRET_KEY environment variable is not set. Exiting.")
        raise RuntimeError("JWT_SECRET_KEY 환경 변수가 설정되지 않았습니다.")
    
    # FastAPI 앱 인스턴스 생성 및 라이프사이클 연결
    app = FastAPI(
        lifespan=app_lifespan,
        docs_url="/docs",
        redoc_url=None,
        title="MyProject API",
        version="1.0.0"
    )
    
    app.add_middleware(LoggingMiddleware)

    # 미들웨어 등록
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 운영 시 도메인 제한 권장
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 세션 미들웨어
    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)

    # JWT 인증 미들웨어
    app.add_middleware(
        JWTBearerMiddleware,
        exempt_paths=exempt_paths,
        exempt_regex_paths=exempt_regex_paths,
        admin_paths=admin_paths,
        admin_regex_paths=admin_regex_paths
    )

    # static 파일 마운트(운영 환경에서만)
    if settings.ENVIRONMENT == "production":
        logger.info("Production environment detected. Mounting /static folder.")
        STATIC_DIR = "/app/static"
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    else:
        logger.info(f"{settings.ENVIRONMENT} environment detected. Skipping /static folder mount.")

    # 라우터 등록
    app.include_router(api_v1_router, prefix="/api/v1")

    logger.info("FastAPI application created and configured successfully.")

    return app

# ==================================
# 4. 앱 인스턴스 생성 및 실행
# ==================================
app = create_app()