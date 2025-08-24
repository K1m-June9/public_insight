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
    

    async def get_organization_summary_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        """
        특정 기관의 요약 정보와 통계를 조회 (집계 정확도 개선 버전)
        """
        try:
            # 1. 서브쿼리 1: 피드 관련 통계 (문서 수, 조회수) - Rating 조인 제거
            feed_stats_subquery = (
                select(
                    Feed.organization_id,
                    func.count(Feed.id).label("total_documents"),
                    func.coalesce(func.sum(Feed.view_count), 0).label("total_views")
                )
                .select_from(Feed)
                .where(Feed.is_active == True)
                .group_by(Feed.organization_id)
            ).subquery()

            # 2. 서브쿼리 2: 평점 관련 통계 (평균 만족도)
            rating_stats_subquery = (
                select(
                    Feed.organization_id,
                    func.coalesce(func.avg(Rating.score), 0.0).label("average_satisfaction")
                )
                .select_from(Feed)
                .join(Rating, Feed.id == Rating.feed_id) # 여기서는 JOIN이 필수
                .where(Feed.is_active == True)
                .group_by(Feed.organization_id)
            ).subquery()

            # 3. 메인 쿼리: Organization 테이블에 두 통계 서브쿼리를 각각 LEFT JOIN
            query = (
                select(
                    Organization.id,
                    Organization.name,
                    Organization.description,
                    Organization.website_url,
                    func.coalesce(feed_stats_subquery.c.total_documents, 0).label("total_documents"),
                    func.coalesce(feed_stats_subquery.c.total_views, 0).label("total_views"),
                    func.coalesce(rating_stats_subquery.c.average_satisfaction, 0.0).label("average_satisfaction")
                )
                .select_from(Organization)
                .outerjoin(
                    feed_stats_subquery, 
                    Organization.id == feed_stats_subquery.c.organization_id
                )
                .outerjoin(
                    rating_stats_subquery, 
                    Organization.id == rating_stats_subquery.c.organization_id
                )
                .where(Organization.name == org_name)
            )

            result = await self.db.execute(query)
            row = result.first()

            if not row:
                return None

            return row._asdict()

        except Exception as e:
            logger.error(f"Error getting organization summary for '{org_name}': {e}", exc_info=True)
            return None
        
    async def get_top_keywords_by_org_name(self, org_name: str, limit: int = 14) -> List[WordCloud]:
        """
        특정 기관의 키워드를 score가 높은 순으로 상위 N개 조회
        
        Args:
            org_name (str): 조회할 기관의 이름
            limit (int): 조회할 최대 키워드 개수
        
        Returns:
            List[WordCloud]: WordCloud(OrganizationKeyword) 모델 객체의 리스트
        """
        try:
            query = (
                select(WordCloud)
                .join(Organization, WordCloud.organization_id == Organization.id)
                .where(Organization.name == org_name)
                .order_by(WordCloud.score.desc())
                .limit(limit)
            )
            result = await self.db.execute(query)
            # SQLAlchemy 모델 객체 자체를 반환하여 서비스 레이어에서 활용하도록 함
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting top keywords for '{org_name}': {e}", exc_info=True)
            return [] # 오류 발생 시 빈 리스트 반환