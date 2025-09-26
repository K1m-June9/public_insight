from sqlalchemy.ext.asyncio import AsyncSession 
from sqlalchemy import select, update, delete 
from app.F6_schemas.admin.app_settings import AppSettingCreateRequest, AppSettingUpdateRequest
from app.F7_models.app_settings import AppSettings 

class AppSettingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db 
    

    async def get_by_key_name(self, key_name: str) -> AppSettings | None:
        stmt = select(AppSettings).where(AppSettings.key_name == key_name)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
    async def create(self, setting_in: AppSettingCreateRequest) -> AppSettings:
        db_setting = AppSettings(**setting_in.model_dump())
        self.db.add(db_setting)
        await self.db.commit()
        await self.db.refresh(db_setting)
        return db_setting 
    
    async def update(self, key_name: str, setting_in: AppSettingUpdateRequest) -> AppSettings | None:
        db_setting = await self.get_by_key_name(key_name)
        if not db_setting:
            return None 
        
        for var, value in setting_in.model_dump(exclude_unset=True).items():
            setattr(db_setting, var, value)
        

        await self.db.commit()
        await self.db.refresh(db_setting)
        return db_setting 
    
    async def get_all(self) -> list[AppSettings]:
        stmt = select(AppSettings)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def delete(self, key_name: str) -> bool:
        db_setting = await self.get_by_key_name(key_name)
        if not db_setting:
            return False 
        await self.db.delete(db_setting)
        await self.db.commit()
        return True 
    