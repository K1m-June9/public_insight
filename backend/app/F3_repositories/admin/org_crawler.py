from sqlalchemy import select 
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any 


from app.F7_models.feeds import Feed, ProcessingStatusEnum, ContentTypeEnum 
from app.F7_models.organizations import Organization
from app.F7_models.categories import Category 
from app.F7_models.app_settings import AppSettings 

class OrgCrawlerTriggerRepository:
    def __init__(self, db:AsyncSession):
        self.db = db

    async def get_source_urls_by_list(self, source_urls: List[str]) -> List[str]:
        """
        주어진 source_urls 리스트에서 이미 DB에 존재하는 URL들을 반환
        어떤 상태로든 DB에 한 번이라도 기록된 source_url은 재수집을 방지하기 위해 이 목록에 포함
        """
        stmt = select(Feed.source_url).where(
            Feed.source_url.in_(source_urls)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_all_active_organizations(self) -> List[Organization]:
        """
        데이터베이스에서 활성 상태(is_active=True)인 모든 기관 목록을 가져옴
        """
        stmt = select(Organization).where(Organization.is_active == True)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_org_with_category_by_name(self, org_name: str) -> Organization | None:
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
    
    async def create_initial_feed(self, data: Dict[str, Any]) -> Feed:
        """
        새로운 피드 레코드를 DB에 초기 상태로 생성
        """
        new_feed = Feed(**data)
        self.db.add(new_feed)
        await self.db.commit()
        await self.db.refresh(new_feed)
        return new_feed
    
    async def update_feed_after_processing(self, feed: Feed, update_data: Dict[str, Any]) -> Feed:
        """
        피드 처리 후 최종 정보를 업데이트합니다.
        """
        for key, value in update_data.items():
            setattr(feed, key, value)
        await self.db.commit()
        await self.db.refresh(feed)
        return feed 
    
    async def update_feed_status(self, feed_id: int, status: ProcessingStatusEnum):
        """
        주어진 ID의 피드 처리 상태를 업데이트
        """
        feed = await self.db.get(Feed, feed_id)
        if feed:
            feed.processing_status = status 
            await self.db.commit()
            await self.db.refresh(feed)

    async def get_by_key_name(self, key_name: str):
        """
        DB 설정 테이블에서 key_name으로 설정 값을 가져옴
        """
        stmt = select(AppSettings).where(AppSettings.key_name == key_name)
        result = await self.db.execute(stmt)
        return result.scalars().first()
    
