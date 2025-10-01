import logging 

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.F8_database.connection import AsyncSessionLocal
from app.F3_repositories.refresh_token import RefreshTokenRepository
from app.F13_recommendations.dependencies import EngineManager
from app.F14_knowledge_graph.pipeline import run_pipeline

logger = logging.getLogger(__name__)

# 스케줄러 인스턴스를 전역으로 생성
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")

# ----- refresh_token 관련 -----
async def cleanup_tokens_task():
    """
    데이터베이스에서 만료된 refresh_token을 주기적으로 자동 삭제하는 스케줄링 작업
    """
    logger.info("Scheduler task 'delete_expired_tokens_task' started.")
    try:
        async with AsyncSessionLocal() as db:
            repo = RefreshTokenRepository(db)
            deleted_count = await repo.delete_expired_and_revoked_tokens()
            if deleted_count > 0:
                logger.info(f"[Scheduler] Deleted {deleted_count} expired refresh tokens.")
            else:
                logger.info("[Scheduler] No expired refresh tokens to delete.")
    except Exception as e:
        logger.error(f"Error in scheduled task 'delete_expired_tokens_task': {e}", exc_info=True)

async def refit_recommendation_engine_task():
    """주기적으로 추천 엔진을 최신 데이터로 재학습시키는 스케줄링 작업"""
    logger.info("Scheduler task 'refit_recommendation_engine_task' started.")
    await EngineManager.refit()
    logger.info("Scheduler task 'refit_recommendation_engine_task' finished.")

def setup_scheduler():
    """
    스케줄러에 작업을 추가하고 시작 준비
    """
    # 매 1시간마다 delete_expired_tokens_task 작업을 실행하도록 추가

    scheduler.add_job(
        cleanup_tokens_task,
        'interval',
        hours=1,
        id="delete_expired_tokens_job",
        name="Cleanup expired and revoked refresh tokens every hour"
    )
    logger.info("Scheduler job 'delete_expired_tokens_task' has been added.")

    # 매일 새벽 3시에 추천 엔진 재학습 작업을 실행
    scheduler.add_job(
        refit_recommendation_engine_task,
        'cron',
        hour=3,
        minute=0,
        id="refit_recommendation_engine_job",
        name="Refit recommendation engine with fresh data daily at 3 AM"
    )
    logger.info("Scheduler job 'refit_recommendation_engine_job' has been added.")

    scheduler.add_job(
        run_pipeline,
        'cron',         # cron 형식으로 시간 지정
        hour=4,         # 매일 새벽 4시
        minute=0,
        id='run_knowledge_graph_pipeline_job', # 작업 고유 ID
        replace_existing=True
    )
    logger.info("Scheduler job 'run_knowledge_graph_pipeline_job' has been added.")


# ----------------------------------------------