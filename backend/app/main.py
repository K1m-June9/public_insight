import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import json
import sys
import ecs_logging 
import uvicorn 

# --- 설정 및 초기화 관련 모듈을 먼저 import ---
from app.F5_core.config import settings 
from app.F10_tasks.scheduler import setup_scheduler, scheduler
from app.F11_search.es_initializer import initialize_elasticsearch
from app.F11_search.ES1_client import es_async, es_sync
from app.F8_database.connection import engine, Base 
from app.F13_recommendations.dependencies import EngineManager
from app.F8_database.graph_db import Neo4jDriver
from app.F14_knowledge_graph.graph_ml import load_node_embeddings

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
class DevFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
    }
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        formatted_message = formatter.format(record)
        
        # extra에 json_fields가 있으면, 그 내용을 JSON으로 변환하여 추가
        if hasattr(record, 'json_fields') and record.json_fields:
            extra_data = json.dumps(record.json_fields, indent=2, ensure_ascii=False)
            formatted_message += f"\n--- EXTRA CONTEXT ---\n{extra_data}\n---------------------"
            
        return formatted_message

def configure_logging():
    """애플리케이션의 모든 로거를 설정"""

    # 기존 로거 핸들러 제거 (중복 출력 방지)
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    
    # 핸들러 및 포맷터 설정
    handler = logging.StreamHandler(sys.stdout)

    # 환경에 따라 포맷터를 다르게 설정
    if settings.ENVIRONMENT == 'production':
        # 운영환경: ECS JSON 포맷터(분석 및 중앙화 로그 수집용)
        formatter = ecs_logging.StdlibFormatter()
        # 운영환경에서는 Uvicorn 로거가 INFO를 찍도로 설정
        # uvicorn_logger = logging.getLogger("uvicorn")
        # uvicorn_logger.setLevel(logging.INFO)

    else:
        # 개발환경: 사람이 읽기 좋은 텍스트 포맷터(터미널에서 디버깅용)
        formatter = DevFormatter()
        # 개발환경에서는 Uvicorn 로거가 DEBUG를 찍도록 설정
        # uvicorn_logger = logging.getLogger("uvicorn")
        # uvicorn_logger.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)

    # .env 파일의 LOG_LEVEL을 동적으로 적용
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # uvicorn, sqlalchemy 등 라이브러리 로그 레벨을 조정
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)


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
    
    # 시작 시 비동기 클라이언트 연결 상태 확인
    try:
        if await es_async.ping():
            logger.info("Successfully pinged Elasticsearch with async client.")
        else:
            logger.warning("Could not ping Elasticsearch with async client.")
    except Exception as e:
        logger.error(f"Async Elasticsearch ping failed on startup: {e}")
    
    #neo4j 연결
    Neo4jDriver.get_driver()

    # 🔧 [신규] 지식 그래프 ML 모델 로딩
    logger.info("Loading Knowledge Graph ML Model...")
    # pipeline.py와 동일한 방식으로 프로젝트 루트 경로를 계산
    project_root_dir = os.path.abspath(__file__)
    # 'main.py'의 위치는 app/ 이므로, 두 단계 위로 올라가면 루트임
    project_root_dir = os.path.dirname(os.path.dirname(project_root_dir))
    embedding_path = os.path.join(project_root_dir, "ml_models", "node_embeddings.pkl")
    
    # 모델 로딩 함수 호출
    model_loaded = load_node_embeddings(embedding_path)
    if not model_loaded:
        logger.warning("Knowledge Graph ML Model could not be loaded. Recommendation features will be disabled.")
    else:
        logger.info("Knowledge Graph ML Model loaded successfully.")

    # 서버 시작 시 추천 엔진을 비동기 최초 학습
    await EngineManager.initial_fit()

    # 스케줄러 설정 및 시작
    setup_scheduler()
    scheduler.start()
    logger.info("APScheduler has been started.")

    yield
    # 종료 시 추가 로직 필요하면 작성

    logger.info("Application shutdown sequence initiated.")
    # 앱 종료 시 redis 연결 종료 등 추가 로직
    # await client_redis.close()
    # await email_redis.close()
    # await token_redis.close()

    # 스케줄러 안전하게 종료
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler has been shut down.")

    # 비동기 Elasticsearch 클라이언트 연결 종료
    if es_async:
        await es_async.close()
        logger.info("Async Elasticsearch connection closed.")

    # 동기 Elasticsearch 클라이언트 연결 종료
    if es_sync:
        es_sync.close()
        logger.info("Sync Elasticsearch connection closed.")

    #neo4j 연결 끗
    await Neo4jDriver.close_driver()

    # await client_redis.close()
    # await email_redis.close()
    # await token_redis.close()

    logger.info("Application shutdown sequence finished.")


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
    app.add_middleware(LoggingMiddleware)
    
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