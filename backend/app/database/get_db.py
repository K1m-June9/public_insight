###___데이터베이스 세션 관리를 담당___###

# 커스텀 모듈
from app.database.init_db import AsyncSessionLocal # 비동기 데이터베이스 세션


# 데이터베이스 세션 생성(FastAPI 의존성 주입)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
# yield session은 세션을 요청 핸들러에게 제공
# session을 yield 하는 순간 FastAPI는 이를 의존성으로 주입
# yield 이후의 코드는 요청 핸들러의 실행이 끝난 후 실행