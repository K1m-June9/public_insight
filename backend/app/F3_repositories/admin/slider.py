from typing import List, Dict, Tuple, Any
import asyncio

from sqlalchemy import select, update, func, case, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BooleanClauseList
from elasticsearch import AsyncElasticsearch 

from app.F7_models.sliders import Slider
import logging

class SliderAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_sliders(self) -> List[Slider]:
        """모든 슬라이더 목록을 display_order 순서로 정렬하여 조회"""
        stmt = select(Slider).order_by(Slider.display_order.asc(), Slider.id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_slider_by_id(self, slider_id: int) -> Slider | None:
        """ID를 기준으로 단일 슬라이더를 조회"""
        stmt = select(Slider).where(Slider.id == slider_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    

    async def create_slider(self, slider_data:dict) -> Slider:
        """
        딕셔너리 형태의 데이터를 받아 새로운 슬라이더를 데이터베이스에 생성, 생성된 Slider 객체를 반환
        """

        new_slider = Slider(**slider_data)

        self.db.add(new_slider)
        await self.db.commit()
        await self.db.refresh(new_slider)
        return new_slider 

    
    async def update_slider(self, slider: Slider, update_data: dict) -> Slider:
        """
        주어진 Slider 객체의 필드를 update_data로 업데이트하고 DB에 커밋
        """
        for key, value in update_data.items():
            setattr(slider, key, value)
        
        # self.db.add(slider)
        await self.db.commit()
        await self.db.refresh(slider)
        return slider
    

    async def update_slider_status(self, slider: Slider, is_active:bool) -> Slider:
        """
        주어진 Slider 객체의 is_active 상태를 업데이트하고 DB에 커밋
        """
        slider.is_active = is_active 

        await self.db.commit()
        await self.db.refresh(slider)
        return slider
    
    async def delete_slider(self, slider:Slider) -> bool:
        """
        주어진 Slider 객체를 DB에서 삭제하고 성공 여부를 반환
        성공 시 True, 실패 시 False
        """
        try:
            await self.db.delete(slider)
            await self.db.commit()
            return True
        except SQLAlchemyError as e:
            await self.db.rollback()
            return False
