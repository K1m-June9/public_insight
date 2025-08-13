import logging

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date

from app.F7_models.organizations import Organization
from app.F7_models.categories import Category
from app.F7_models.feeds import Feed
from app.F7_models.word_clouds import WordCloud
from app.F7_models.bookmarks import Bookmark
from app.F7_models.ratings import Rating

logger = logging.getLogger(__name__)

class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 활성화된 기관 목록과 각 기관별 피드 개수 조회 메서드
    # 입력: 없음
    # 반환: 
    #   기관 정보와 피드 개수가 포함된 딕셔너리 리스트
    #   [{"organization_id": int, "organization_name": str, "feed_count": int}, ...]
    # 설명: 
    #   활성화된 기관(is_active=True)과 해당 기관의 활성화된 피드 개수를 집계하여 반환
    #   LEFT JOIN을 사용하여 피드가 없는 기관도 포함 (feed_count=0으로 표시)
    #   기관 ID 오름차순으로 정렬하여 일관된 순서 보장
    #   성능 최적화를 위해 단일 쿼리로 모든 데이터 처리
    async def get_organizations_with_feed_counts(self) -> List[Dict[str, Any]]:
        # LEFT JOIN을 사용하여 기관과 피드를 연결하고 피드 개수 집계
        # 활성화된 기관만 조회하되, 피드가 없는 기관도 포함
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                func.count(Feed.id).label('feed_count')
            )
            .select_from(Organization)
            .outerjoin(Feed, and_(Organization.id == Feed.organization_id, Feed.is_active == True))
            .where(Organization.is_active == True)
            .group_by(Organization.id, Organization.name)
            .order_by(Organization.id.asc())
        )
        result = await self.db.execute(query)
        return [row._asdict() for row in result.all()]

    # 기관명으로 해당 기관의 카테고리 목록과 각 카테고리별 피드 개수 조회 메서드 ('보도자료' 제외)
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   기관 정보와 카테고리별 피드 개수가 포함된 딕셔너리 또는 None
    #   {"organization": {"id": int, "name": str}, "categories": [{"category_id": int, "category_name": str, "feed_count": int}, ...]}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하고, 해당 기관의 활성화된 카테고리와 각 카테고리별 활성화된 피드 개수를 집계
    #   '보도자료' 카테고리는 원형 그래프 구성에서 제외하므로 조회 대상에서 제외
    #   LEFT JOIN을 사용하여 피드가 없는 카테고리도 포함 (feed_count=0으로 표시)
    #   카테고리 ID 오름차순으로 정렬하여 일관된 순서 보장
    #   존재하지 않는 기관이거나 활성화된 카테고리가 없는 경우 None 반환
        # 기관, 카테고리, 피드를 JOIN하여 카테고리별 피드 개수 집계
        # 기관명으로 조회하되 기관 활성화 상태는 확인하지 않음
        # 활성화된 카테고리 중 '보도자료'를 제외하고 활성화된 피드만 대상으로 함
    async def get_categories_with_feed_counts_by_org_name(self, org_name: str) -> List[Dict[str, Any]]:
        # 기관, 카테고리, 피드를 JOIN하여 카테고리별 피드 개수 집계
        # 기관명으로 조회하되 기관 활성화 상태는 확인하지 않음
        # 활성화된 카테고리 중 '보도자료'를 제외하고 활성화된 피드만 대상으로 함
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                Category.id.label('category_id'),
                Category.name.label('category_name'),
                func.count(Feed.id).label('feed_count')
            )
            .select_from(Organization)
            .join(Category, Organization.id == Category.organization_id)
            .outerjoin(Feed, and_(Category.id == Feed.category_id, Feed.is_active == True))
            .where(
                Organization.name == org_name,
                Category.is_active == True,
                Category.name != '보도자료'
            )
            .group_by(Organization.id, Organization.name, Category.id, Category.name)
            .order_by(Category.id.asc())
        )
        result = await self.db.execute(query)
        return [row._asdict() for row in result.all()]

    # 기관명으로 기관 정보 조회 메서드 (아이콘 표시용)
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   기관 정보가 포함된 딕셔너리 또는 None
    #   {"id": int, "name": str, "website_url": str, "icon_path": str}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하여 아이콘 표시에 필요한 기본 정보 반환
    #   기관의 활성화 상태와 무관하게 조회 (name 조건만 사용)
    #   존재하지 않는 기관인 경우 None 반환하여 Service 레이어에서 처리
    #   Service 레이어에서 Base64 인코딩 및 스키마 변환에 활용
    async def get_organization_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        # 기관명으로 기관 기본 정보 조회
        # 아이콘 표시에 필요한 필드만 선택하여 성능 최적화
        query = select(
            Organization.id,
            Organization.name,
            Organization.website_url,
            Organization.icon_path
        ).where(Organization.name == org_name)
        result = await self.db.execute(query)
        row = result.first()
        return row._asdict() if row else None

    # 기관명으로 해당 기관의 최근 2개년 워드클라우드 데이터 조회 메서드
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    #   current_date - 현재 날짜 (date)
    # 반환: 
    #   기관 정보와 워드클라우드 데이터가 포함된 딕셔너리 또는 None
    #   {"organization": {"id": int, "name": str}, "wordclouds": [{"cloud_data": list, "period_start": date, "period_end": date, "created_at": datetime}, ...]}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하고, 현재 날짜 기준 최근 2개년의 워드클라우드 데이터를 반환
    #   period_start의 연도를 기준으로 최근 2개년 필터링 (예: 2025년 → 2024, 2025년 데이터)
    #   생성일 기준 내림차순 정렬하여 최신 데이터 우선 반환
    #   존재하지 않는 기관이거나 워드클라우드 데이터가 없는 경우 None 반환
    async def get_organization_wordclouds_by_name(self, org_name: str, current_date: date) -> List[Dict[str, Any]]:
        current_year = current_date.year
        target_years = [current_year, current_year - 1] #최근 2개년
        
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                WordCloud.cloud_data,
                WordCloud.period_start,
                WordCloud.period_end,
                WordCloud.created_at
            )
            .select_from(Organization)
            .join(WordCloud, Organization.id == WordCloud.organization_id)
            .where(
                Organization.name == org_name,
                func.year(WordCloud.period_start).in_(target_years)
            )
            .order_by(WordCloud.created_at.desc())
        )
        result = await self.db.execute(query)
        return [row._asdict() for row in result.all()]
    

    async def get_organization_summary_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        """
        특정 기관의 요약 정보와 통계를 조회
        (기관 정보 + 총 문서 수 + 총 조회수 + 평균 별점)
        
        Args:
            org_name (str): 조회할 기관의 이름
        
        Returns:
            Optional[Dict[str, Any]]: 기관 요약 정보 딕셔너리 또는 None
        """
        try:
            # 1. 서브쿼리: 해당 기관에 속한 모든 피드의 평균 별점을 계산
            #    COALESCE를 사용하여 평점이 없는 경우 0.0을 반환
            avg_rating_subquery = (
                select(
                    func.coalesce(func.avg(Rating.score), 0.0).label('average_satisfaction')
                )
                .select_from(Feed)
                .join(Rating, Feed.id == Rating.feed_id)
                .join(Organization, Feed.organization_id == Organization.id)
                .where(Organization.name == org_name, Feed.is_active == True)
            ).scalar_subquery()

            # 2. 메인 쿼리: 기관 정보와 나머지 통계를 집계
            query = (
                select(
                    Organization.id,
                    Organization.name,
                    Organization.description,
                    Organization.website_url,
                    func.count(Feed.id).label('total_documents'),
                    func.coalesce(func.sum(Feed.view_count), 0).label('total_views'),
                    avg_rating_subquery.label('average_satisfaction')
                )
                .select_from(Organization)
                .outerjoin(Feed, and_(Organization.id == Feed.organization_id, Feed.is_active == True))
                .where(
                    Organization.name == org_name,
                    Organization.is_active == True
                )
                .group_by(
                    Organization.id,
                    Organization.name,
                    Organization.description,
                    Organization.website_url
                )
            )

            result = await self.db.execute(query)
            row = result.first()

            if not row:
                return None

            return row._asdict()

        except Exception as e:
            logger.error(f"Error getting organization summary for '{org_name}': {e}", exc_info=True)
            # 리포지토리에서는 예외를 다시 발생시켜 서비스 레이어에서 처리할수도 있음
            # 지금은 None을 반환하여 서비스에서 처리
            return None