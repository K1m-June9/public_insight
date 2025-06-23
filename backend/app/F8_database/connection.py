from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from app.F5_core.config import settings


# 비동기 SQLAlchemy 엔진 생성
engine = create_async_engine(settings.DATABASE_URL, echo=True, poolclass=NullPool)

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
