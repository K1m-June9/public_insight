from fastapi import Depends
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Set, Optional, Dict
from sqlalchemy.orm import selectinload, joinedload

from app.F7_models.feeds import Feed, ProcessingStatusEnum
from app.F7_models.organizations import Organization
from app.F7_models.app_settings import AppSettings

class OrgCrawlerRepository:
    def __init__(self, db:AsyncSession):
        self.db = db

    # --- Feed 관련 메소드들 ---
    async def get_source_urls_by_list(self, urls: List[str]) -> Set[str]:
        """주어진 URL 리스트 중 DB에 이미 존재하는 source_url들만 집합으로 반환"""
        if not urls:
            return set()
        
        stmt = select(Feed.source_url).where(Feed.source_url.in_(urls))
        result = await self.db.execute(stmt)
        return {row[0] for row in result.all()}

    async def create_initial_feed(self, feed_data: dict) -> Feed:
        """초기 피드 데이터를 받아 DB에 생성하고, 생성된 객체를 반환"""
        new_feed = Feed(**feed_data)
        self.db.add(new_feed)
        await self.db.commit()
        await self.db.refresh(new_feed)
        return new_feed
    
    async def update_feed_after_processing(self, feed: Feed, update_data: dict) -> Feed:
        """2차 처리(요약, 파일 저장 등)가 끝난 후 피드 정보를 업데이트"""
        for key, value in update_data.items():
            setattr(feed, key, value)
        
        await self.db.commit()
        await self.db.refresh(feed)
        return feed 
    
    async def update_feed_status(self, feed_id: int, status: ProcessingStatusEnum):
        """피드의 처리 상태만 업데이트"""
        stmt = select(Feed).where(Feed.id == feed_id)
        result = await self.db.execute(stmt)
        feed_to_update = result.scalar_one_or_none()
        if feed_to_update:
            feed_to_update.processing_status = status 
            await self.db.commit()

    async def delete_feed(self, feed_id: int) -> bool:
        """Feed ID로 피드 삭제"""
        try:
            stmt = delete(Feed).where(Feed.id == feed_id)
            await self.db.execute(stmt)
            await self.db.commit()
            return True 
        except Exception as e:
            await self.db.rollback()
            return False
        
    # --- Organization 관련 메소드들 ----
    async def get_org_with_category_by_name(self, name: str) -> Optional[Organization]:
        """기관 이름으로 Organization 객체를 연관 Category와 함께 조회"""
        stmt = select(Organization).where(Organization.name == name).options(
            selectinload(Organization.categories)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    

    # --- AppSettings 관련 메소드들 ---
    async def get_by_key_name(self, key_name: str) -> AppSettings | None:
        stmt = select(AppSettings).where(AppSettings.key_name == key_name)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    

    # --- 카테고리 조회 ---
    async def get_org_with_policy_material_categories(self, org_name: str) -> Organization | None:
        """
        기관 이름으로 기관과 연결된 카테고리를 함께 가져옴
        - '보도자료'와 '정책뉴스' 카테고리는 제외
        """
        stmt = (
            select(Organization)
            .options(joinedload(Organization.categories))
            .where(Organization.name == org_name)
        )
        result = await self.db.execute(stmt)
        org = result.scalars().first()

        if org: 
            excluded_categories = {"보도자료", "정책뉴스"}
            org.categories = [c for c in org.categories if c.name not in excluded_categories]
        return org