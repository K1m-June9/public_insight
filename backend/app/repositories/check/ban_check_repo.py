from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 커스텀 모듈
from app.models.ban import restriction_history, banned_keywords

# ID 금칙어 체크 
async def repo_id_banned_keywords(db: AsyncSession, username_parts: list) -> bool:
    for username_word in username_parts:
        result = await db.execute(select(banned_keywords).where(banned_keywords.keyword == username_word))
        record = result.scalars().first()

        # 금칙어가 하나라도 발견되면 False 반환
        if record is not None:
            return False
    # 금칙어가 없거나 테이블이 비어 있으면 True 반환
    return True


# Nickname 금칙어 체크
async def repo_nickname_banned_keywords(db: AsyncSession, nickname: str) -> bool:
    result = await db.execute(select(banned_keywords).where(banned_keywords.keyword == nickname))
    record = result.scalars().first()

    # 금칙어가 없거나 테이블이 비어 있으면 True 반환
    return record is None
