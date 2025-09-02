from functools import lru_cache
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.F8_database.session import get_db, AsyncSessionLocal
from app.F13_recommendations.engine import RecommendationEngine
from app.F13_recommendations.repository import RecommendationRepository
from app.F13_recommendations.service import RecommendationService
from app.F7_models.feeds import Feed

logger = logging.getLogger(__name__)

# --- 싱글톤 추천 엔진 ---
@lru_cache()
def get_recommendation_engine() -> RecommendationEngine:
    """
    싱글톤 RecommendationEngine 인스턴스를 생성하고 반환함.
    최초 호출 시 DB에서 모든 피드 데이터를 가져와 엔진을 학습시킴.
    """
    logger.info("Initializing RecommendationEngine singleton...")
    engine = RecommendationEngine()
    
    # 비동기 함수(get_all_feeds_for_fitting)를 동기 함수(@lru_cache) 내에서
    # 직접 await할 수 없으므로, 별도의 동기 세션을 생성하여 데이터를 가져와야 함.
    # 혹은 서버 시작 시점에 이벤트를 통해 비동기적으로 로드하는 방법도 있음.
    # 여기서는 가장 간단한 방법인, 독립적인 비동기 I/O 루프를 사용하는 방식을 택함.
    try:
        import asyncio
        # asyncio.run()은 이미 실행 중인 루프에서 호출할 수 없으므로,
        # get_event_loop().run_until_complete()를 사용하거나,
        # 간단하게는 별도의 DB 연결 로직을 구성해야 함.

        # 가장 간단하고 안전한 방법: 서버 시작 시점에 이 함수가 호출될 것을 가정하고,
        # 별도의 비동기 세션을 생성하여 데이터를 로드함.
        async def _fit_engine():
            logger.info("Attempting to fit the recommendation engine...")
            async with AsyncSessionLocal() as session:
                repo = RecommendationRepository(db=session)
                all_feeds = await repo.get_all_feeds_for_fitting()
                engine.fit(all_feeds)
            logger.info("Recommendation engine fitted successfully.")

        # 비동기 함수를 동기적으로 실행
        asyncio.run(_fit_engine())

    except Exception as e:
        logger.error(f"Failed to initialize and fit recommendation engine: {e}", exc_info=True)
        # 엔진 학습에 실패하더라도 서버가 중단되지 않도록 함.
        # 이 경우, 엔진은 학습되지 않은 상태로 남아있게 됨.
    
    return engine


# --- 의존성 주입 함수들 ---
def get_recommendation_repository(db: AsyncSession = Depends(get_db)) -> RecommendationRepository:
    return RecommendationRepository(db=db)

def get_recommendation_service(
    repo: RecommendationRepository = Depends(get_recommendation_repository),
    engine: RecommendationEngine = Depends(get_recommendation_engine)
) -> RecommendationService:
    return RecommendationService(repo=repo, engine=engine)