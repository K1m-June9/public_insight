from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 커스텀 모듈
from app.models.user import user_table

# user id 중복 체크
async def repo_id_exists(db: AsyncSession, username: str) -> bool:
    result = await db.execute(select(user_table).where(user_table.username == username))
    record = result.scalars().first()
    # 테이블이 비어있거나 중복이 없으면 True
    return record is None

# 닉네임 중복 체크
async def repo_nickname_exists(db: AsyncSession, nickname: str) -> bool:
    result = await db.execute(select(user_table).where(user_table.nickname == nickname))
    record = result.scalars().first()
    return record is None


# 이메일 중복 체크 
async def repo_email_exists(db: AsyncSession, email: str) -> bool:
    result = await db.execute(select(user_table).where(user_table.email == email))
    record = result.scalars().first()
    return record is None

