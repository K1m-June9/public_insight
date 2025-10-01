import logging
import asyncio
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.F8_database.session import get_db, AsyncSessionLocal
from app.F13_recommendations.engine import RecommendationEngine
from app.F13_recommendations.repository import RecommendationRepository
from app.F13_recommendations.service import RecommendationService

logger = logging.getLogger(__name__)

class EngineManager:
    """
    RecommendationEngine의 생명주기를 관리하는 싱글톤 매니저.
    """
    _engine: RecommendationEngine = None

    @classmethod
    def get_engine(cls) -> RecommendationEngine:
        """싱글톤 엔진 인스턴스를 반환함."""
        if cls._engine is None:
            logger.info("EngineManager: Engine instance is not created yet. Creating a new one.")
            cls._engine = RecommendationEngine()
        return cls._engine

    @classmethod
    async def initial_fit(cls):
        """[비동기] 서버 시작 시 엔진을 최초로 학습시킴."""
        engine = cls.get_engine()
        if engine.feeds:
            logger.info("EngineManager: Engine is already fitted. Skipping initial fit.")
            return

        logger.info("EngineManager: Starting initial fit of the recommendation engine.")
        try:
            async with AsyncSessionLocal() as session:
                repo = RecommendationRepository(db=session)
                all_feeds = await repo.get_all_feeds_for_fitting()
                engine.fit(all_feeds)
        except Exception as e:
            logger.error(f"EngineManager: Failed during initial fit. Engine might be empty. Error: {e}", exc_info=True)

    @classmethod
    async def refit(cls):
        """[비동기] 스케줄러에 의해 호출될 엔진 재학습 메서드."""
        engine = cls.get_engine()
        logger.info("EngineManager: Starting scheduled refit of the recommendation engine.")
        try:
            async with AsyncSessionLocal() as session:
                repo = RecommendationRepository(db=session)
                all_feeds = await repo.get_all_feeds_for_fitting()
                engine.refit(all_feeds)
        except Exception as e:
            logger.error(f"EngineManager: Failed during scheduled refit. Error: {e}", exc_info=True)


# --- 의존성 주입 함수들 ---
# 이제 get_recommendation_engine은 EngineManager를 통해 엔진을 가져옴
def get_recommendation_engine() -> RecommendationEngine:
    return EngineManager.get_engine()

def get_recommendation_repository(db: AsyncSession = Depends(get_db)) -> RecommendationRepository:
    return RecommendationRepository(db=db)

def get_recommendation_service(
    repo: RecommendationRepository = Depends(get_recommendation_repository),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
) -> RecommendationService:
    return RecommendationService(repo=repo, engine=engine)