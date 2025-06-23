### 임시 ###
"""
데이터베이스에서 만료된 refresh_token을 주기적으로 자동 삭제
"""

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from app.F8_database.connection import AsyncSessionLocal
# from app.F3_repositories.refresh_token import RefreshTokenRepository
# import asyncio

# # APScheduler 인스턴스 생성
# scheduler = AsyncIOScheduler()

# # 만료된 Refresh Token 삭제 작업 정의
# async def delete_expired_tokens_task():
#     async with AsyncSessionLocal() as db:
#         repo = RefreshTokenRepository(db)
#         deleted_count = await repo.delete_expired_tokens()
#         print(f"[Scheduler] Deleted expired tokens: {deleted_count}")

# # 스케줄러 시작 함수 (FastAPI 앱 실행 시 호출되어야 함)
# def start_scheduler():
#     scheduler.add_job(delete_expired_tokens_task, 'interval', hours=1)  # 매 1시간마다 실행
#     scheduler.start()
