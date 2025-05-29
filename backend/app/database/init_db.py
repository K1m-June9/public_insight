###___데이터베이스 접속, 세션 생성, Base 선언___###

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 비동기 세션 팩토리
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)

# Base 클래스 정의
Base = declarative_base()
