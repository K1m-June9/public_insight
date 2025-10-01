import logging
from neo4j import AsyncGraphDatabase, AsyncDriver
from contextlib import asynccontextmanager

from app.F5_core.config import settings

logger = logging.getLogger(__name__)

class Neo4jDriver:
    """
    Neo4j AsyncDriver의 싱글톤 인턴스를 관리하는 클래스.
    앱 생명주기와 함께 연결을 관리함.
    """
    _driver: AsyncDriver = None

    @classmethod
    def get_driver(cls) -> AsyncDriver:
        """싱글톤 드라이버 인스턴스를 반환함."""
        if cls._driver is None:
            logger.info("Initializing Neo4j driver...")
            try:
                cls._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
                )
                logger.info("Neo4j driver initialized successfully.")
            except Exception as e:
                logger.error(f"Failed to initialize Neo4j driver: {e}", exc_info=True)
                raise
        return cls._driver

    @classmethod
    async def close_driver(cls):
        """앱 종료 시 드라이버 연결을 닫음."""
        if cls._driver is not None:
            logger.info("Closing Neo4j driver...")
            await cls._driver.close()
            cls._driver = None
            logger.info("Neo4j driver closed.")

@asynccontextmanager
async def get_neo4j_session():
    """
    FastAPI 의존성 주입을 위한 Neo4j 세션 컨텍스트 매니저.
    SQLAlchemy의 get_db와 유사한 역할을 함.
    """
    driver = Neo4jDriver.get_driver()
    if not driver:
        raise RuntimeError("Neo4j driver is not available.")
    
    # 비동기 세션을 열고, 요청 핸들러에 제공(yield)
    async with driver.session() as session:
        yield session