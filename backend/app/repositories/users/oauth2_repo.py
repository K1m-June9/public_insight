from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy import or_
import logging

# 커스텀 모듈
from app.models.user import user_table
from app.models.ouath2_token import device_info, refresh_tokens

logger = logging.getLogger(__name__)


# USER ID 찾기
async def repo_id_get(username:str, db:AsyncSession):
    result = await db.execute(select(user_table).where(user_table.username == username))
    stmt = (
        select(user_table)
        .options(selectinload(user_table.devices))  # 디바이스 정보도 함께 로드
        .where(user_table.username == username)

    )
    result = await db.execute(stmt)
    record = result.scalars().first()
    return record 


# 디바이스 정보 가져오기(없다면 저장)
async def repo_device_get_or_create(username:str, device_name:str, db:AsyncSession):
    stmt = select(device_info).where(device_info.username == username, device_info.device_name == device_name)
    result = await db.execute(stmt)
    record = result.scalars().first()

    if not record:
        new_device = device_info(
            username=username,
            device_name=device_name    
        )
        db.add(new_device)
        await db.commit()
        await db.refresh(new_device)
        return new_device
    
    return record



# Refresh Token 생성 및 갱신
# 새로 생성시 True
# 업데이트 시 False
async def repo_refresh_token_update_or_create(device_id:str, refresh_token: str, expires_at: datetime, db:AsyncSession):
    stmt = select(refresh_tokens).where(refresh_tokens.device_id == device_id)
    result = await db.execute(stmt)
    record = result.scalars().first()

    if record:
        record.refresh_token = refresh_token 
        record.expires_at = expires_at
        created = False
    else:
        new_token = refresh_tokens(device_id=device_id, refresh_token=refresh_token, expires_at=expires_at)
        db.add(new_token)
        created = True

    await db.commit()
    return created


# 로그아웃으로 Refresh Token 삭제
async def repo_refresh_token_delete(device_id: str, db:AsyncSession):
    stmt= select(refresh_tokens).where(refresh_tokens.device_id == device_id)
    result = await db.execute(stmt)
    record = result.scalars().first()

    if record:
        await db.delete(record)
        await db.commit()
        return True
    return False


# Refresh Token 유효성 검증
# refresh_token으로 조회
async def repo_refresh_token_get_by_token(refresh_token: str, db: AsyncSession):
    stmt = select(refresh_tokens).where(refresh_tokens.refresh_token == refresh_token)
    result = await db.execute(stmt)
    return result.scalars().first()

# device_id로 조회
async def repo_refresh_token_get_by_device(device_id: str, db: AsyncSession):
    stmt = select(refresh_tokens).where(refresh_tokens.device_id == device_id)
    result = await db.execute(stmt)
    return result.scalars().first()


# Refresh 시 재사용 방지용 삭제
# 삭제 성공 시: True
# 삭제 대상 없을 시 : False
async def repo_use_refresh_token(token:str, db:AsyncSession):
    stmt = select(refresh_tokens).where(refresh_tokens.refresh_token == token)
    result = await db.execute(stmt)
    record = result.scalars().first()

    if record:
        try:
            await db.delete(record)
            await db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to delete refresh token: {e}", exc_info=True)
            raise
    return False


# username 가져오기
async def repo_device_get(device_id:str, db:AsyncSession):
    stmt = select(device_info).where(device_info.device_id == device_id)
    result = await db.execute(stmt)
    record = result.scalars().first()
    return record