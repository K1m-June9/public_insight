from typing import List, Dict, Tuple, Any
import asyncio

from sqlalchemy import select, update, func, case, or_, and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BooleanClauseList
from elasticsearch import AsyncElasticsearch 

from app.F7_models.notices import Notice
import logging

class NoticesAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_notices(self) -> List[Notice]:
        """
        모든 공지사항을 조회하되, 다음 조건에 따라 정렬 반환
        1. [최우선] 고정 공지사항(is_pinned = True)이 최상단에 오도록 정렬
        2. [2순위] 모든 공지사항은 생성일 기준(created_at) 내림차순(desc)으로 정렬
        """

        stmt = select(Notice).order_by(
            Notice.is_pinned.desc(),  # 1순위: 고정 여부 (True가 먼저)
            Notice.created_at.desc() # 2순위: 생성 날짜 (최신이 먼저)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()
    

    async def get_notice_by_id(self, notice_id:int) -> Notice | None:
        """ID를 기준으로 단일 공지사항 조회"""
        stmt = select(Notice).where(Notice.id == notice_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_notice(self, notice_data:dict) -> Notice:
        """
        딕셔너리 형태의 데이터를 받아 새로운 공지사항을 데이터베이스에 생성, 생성된 Notice 객체를 반환
        """
        new_notice = Notice(**notice_data)

        self.db.add(new_notice)
        return new_notice
    
    async def update_notice(self,notice:Notice ,update_data:dict) -> Notice:
        """
        주어진 Notice 객체를 update_data로 업데이트하고 DB에 커밋
        """
        for key, value in update_data.items():
            setattr(notice, key, value)

        return notice
    
    async def delete_notice(self, notice:Notice) -> bool:
        """
        주어진 Notice 객체를 DB에서 삭제하고 성공 여부를 반환
        """
        try: 
            await self.db.delete(notice)
            return True
        
        except SQLAlchemyError as e:
            return False