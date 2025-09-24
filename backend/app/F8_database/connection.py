from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager 
from typing import AsyncGenerator

from app.F5_core.config import settings


# ============================================================
# 비동기 SQLAlchemy 엔진 생성 (UTF-8 설정 강화)
# ============================================================
engine = create_async_engine(
    settings.DATABASE_URL, 
    echo=True, 
    poolclass=NullPool,
    connect_args={"charset": "utf8mb4"} 
    )

# ============================================================
# 비동기 세션 팩토리
# ============================================================
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)

# ============================================================
# Base 클래스 정의
# ============================================================
Base = declarative_base()


# ============================================================
# 세션 컨텍스트 매니저 (API 요청/응답 사이클 외부에서 안전하게 사용)
# ============================================================
@asynccontextmanager
async def async_session_scope() -> AsyncGenerator[AsyncSession, None]:
    """
    API 요청/응답 사이클 외부에서 안전하게 DB 세션을 생성하고 닫기 위한 비동기 컨텍스트 매니저
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise 
    finally:
        await session.close()
        