from app.F8_database.connection import AsyncSessionLocal
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

# 데이터베이스 세션 생성(FastAPI 의존성 주입)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"DB 세션 오류: {e}")
            raise
# yield session은 세션을 요청 핸들러에게 제공
# session을 yield 하는 순간 FastAPI는 이를 의존성으로 주입
# yield 이후의 코드는 요청 핸들러의 실행이 끝난 후 실행

@asynccontextmanager
async def get_standalone_session():
    """의존성 주입과 별개로 독립적인 DB 세션을 생성하는 컨텍스트 매니저"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise