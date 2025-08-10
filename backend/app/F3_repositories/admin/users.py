from typing import List, Dict, Tuple, Any
import asyncio

from sqlalchemy import select, update, func, case, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BooleanClauseList
from elasticsearch import AsyncElasticsearch 

import logging


from app.F7_models.users import User
from app.F7_models.bookmarks import Bookmark 
from app.F7_models.ratings import Rating 
from app.F6_schemas.admin.users import (
    UserListRequest,
    UserManagement, 
    UserRole,
    UserStatus
)

logger = logging.getLogger(__name__)

class UsersAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_total_user_count(self) -> int:
        """전체 사용자 수를 조회"""
        stmt = select(func.count(User.id))
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def get_user_counts_by_role(self) -> Dict[UserRole, int]:
        """역할(role)별 사용자 수를 조회"""
        stmt = select(User.role, func.count(User.id)).group_by(User.role)
        result = await self.db.execute(stmt)
        return {role: count for role, count in result.all()}

    async def get_user_counts_by_status(self) -> Dict[str, int]:
        """상태별 사용자 수를 조회"""
        stmt = select(User.status, func.count(User.id)).group_by(User.status)
        result = await self.db.execute(stmt)
        return {status: count for status, count in result.all()}
    
    async def get_filtered_user_count(self, params: UserListRequest) -> int:
        """필터링 조건이 적용된 사용자의 총 수를 조회"""
        stmt = select(func.count(User.id))
        conditions = self._build_filter_conditions(params)

        if conditions:
            stmt = stmt.where(*conditions)
        result = await self.db.execute(stmt)
        return result.scalar_one()
        
    
    async def get_paginated_user_list(self, params: UserListRequest) -> List[User]:
        """필터링, 정렬, 페이지네이션이 적용된 사용자 목록을 조회"""
        stmt = select(User)
        
        # 조건 필터링
        conditions = self._build_filter_conditions(params)
        if conditions:
            stmt = stmt.where(*conditions)
        
        # 역할 우선순위 기반 정렬
        role_priority = case(UserManagement.ROLE_PRIORITY, value=User.role, else_=99)
        stmt = stmt.order_by(role_priority.asc(), User.user_id.asc())
        
        # 페이지네이션
        offset = (params.page - 1) * params.limit
        stmt = stmt.offset(offset).limit(params.limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    #==============================
    # 내부 유틸 메서드
    #============================== 
    def _build_filter_conditions(self, params: UserListRequest) -> List[BooleanClauseList]:
        """
        요청 파라미터를 기반으로 WHERE 절에 들어갈 조건 리스트를 생성합니다.
        """
        conditions = []
        if params.role:
            conditions.append(User.role == params.role)
        if params.status:
            conditions.append(User.status == params.status)
        if params.search:
            search_term = f"%{params.search}%"
            # 대소문자 구분 없는 LIKE 검색
            conditions.append(
                or_(
                    User.user_id.ilike(search_term),
                    User.nickname.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        return conditions
    
    # id로 설계한건지, uer_id로 설계한건지 확인할 것
    async def get_user_by_id(self, user_id: str) -> User | None:
        """ID를 기준으로 단일 사용자를 조회"""
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_rdb_user_statistics(self, user_id: str) -> dict:
        """"""
        stmt_bookmarks = select(func.count(Bookmark.id)).where(Bookmark.user_id == user_id)
        stmt_ratings = select(func.count(Rating.id)).where(Rating.user_id == user_id)

        result = await asyncio.gather(
            self.db.execute(stmt_bookmarks),
            self.db.execute(stmt_ratings)
        )

        return {
            "total_bookmarks":result[0].scalar_one(),
            "total_ratings":result[1].scalar_one()            
        }
    
    async def update_user_role(self, user_id:str, new_role:UserRole) -> User | None:
        """특정 사용자의 역할을 변경하고, 변경된 사용자 객체를 반환"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(role=new_role, updated_at=func.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_user_by_id(user_id)

    async def update_user_status(self, user_id: str, new_status:UserStatus) -> User | None:
        """특정 사용자의 상태를 변경하고, 변경된 사용자 객체를 반환"""
        stmt = (
            update(User)
            .where(User.user_id == user_id)
            .values(status=new_status, updated_at=func.now())
        )
        await self.db.execute(stmt)
        await self.db.commit()
        return await self.get_user_by_id(user_id)
    
