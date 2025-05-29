###___main.py___###

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

# 커스텀 모듈
from app.database.init_db import engine, Base 
from app.routers import api_router
from app.routers.api_router import api_router

# 애플리케이션 시작 시 테이블을 자동으로 생성하는 로직
@asynccontextmanager
async def app_lifespan(app: FastAPI):
    # 애플리케이션 시작 시 실행될 로직
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield 
    # 애플리케이션 종료 시 실행될 로직

# 환경 변수 로드
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY 환경 변수가 설정되지 않았습니다.")


# FastAPI 애플리케이션 초기화
app = FastAPI(lifespan=app_lifespan)
# docs_url=None, redoc_url=None
# Swagger UI와 Redoc를 배포시에는 ***비활성화***

# 세션 미들웨어 추가
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY) #secret_key는 암호화 키로 임의로 설정

# API 라우터 등록
app.include_router(api_router)      