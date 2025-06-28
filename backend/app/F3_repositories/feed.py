from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging
from app.F7_models.feeds import Feed
from app.F7_models.ratings import Rating
from app.F7_models.organizations import Organization
from app.F7_models.categories import Category

logger = logging.getLogger(__name__)

class FeedRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 피드 목록과 관련 정보 통합 조회 메서드
    # 입력: 없음
    # 반환: 
    #   피드 상세 정보가 포함된 Dict 객체들의 리스트
    #   각 Dict는 피드 기본 정보, 기관 정보, 평균 별점을 포함
    # 설명: 
    #   활성화된 피드들을 기관 정보와 평균 별점과 함께 조회
    #   LEFT JOIN을 사용하여 한 번의 쿼리로 모든 필요한 데이터를 가져옴
    #   published_date 기준 내림차순으로 정렬하여 최신 피드부터 반환
    #   평점이 없는 피드의 경우 average_rating은 None으로 처리
    async def get_feeds_with_details(self) -> List[Dict[str, Any]]:
        # 피드, 기관, 평균별점을 한 번에 조회하는 JOIN 쿼리 구성
        query = select(
            Feed.id,
            Feed.title,
            Feed.summary,
            Feed.published_date,
            Feed.view_count,
            Feed.organization_id,
            Organization.name.label('organization_name'),
            func.avg(Rating.score).label('average_rating')
        ).select_from(
            # 피드 테이블을 기준으로 LEFT JOIN 수행
            Feed.__table__.join(
                Organization.__table__, 
                Feed.organization_id == Organization.id
            ).outerjoin(
                Rating.__table__, 
                Feed.id == Rating.feed_id
            )
        ).where(
            # 활성화된 피드만 조회
            Feed.is_active == True
        ).group_by(
            # 평균 별점 계산을 위한 그룹화
            Feed.id,
            Feed.title,
            Feed.summary,
            Feed.published_date,
            Feed.view_count,
            Feed.organization_id,
            Organization.name
        ).order_by(
            # 발행일 기준 최신순 정렬
            Feed.published_date.desc()
        )
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'summary': row.summary,
                'published_date': row.published_date,
                'view_count': row.view_count,
                'organization_id': row.organization_id,
                'organization_name': row.organization_name,
                'average_rating': float(row.average_rating) if row.average_rating is not None else None
            }
            feeds_data.append(feed_dict)
        
        return feeds_data
    
    # 기관별 피드 목록과 관련 정보 통합 조회 메서드
    # 입력: 
    #   organization_name - 조회할 기관명 (str)
    #   category_id - 필터링할 카테고리 ID (int, 선택적)
    # 반환: 
    #   피드 상세 정보가 포함된 Dict 객체들의 리스트
    #   각 Dict는 피드 기본 정보, 기관 정보, 카테고리 정보, 평균 별점을 포함
    # 설명: 
    #   특정 기관의 활성화된 피드들을 카테고리 정보와 평균 별점과 함께 조회
    #   '보도자료' 카테고리는 항상 제외 (별도 API에서 처리)
    #   category_id가 제공된 경우 해당 카테고리로 추가 필터링
    #   published_date 기준 내림차순으로 정렬하여 최신 피드부터 반환
    #   평점이 없는 피드의 경우 average_rating은 None으로 처리
    async def get_feeds_by_organization_name(self, organization_name: str, category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        # 피드, 기관, 카테고리, 평균별점을 한 번에 조회하는 JOIN 쿼리 구성
        query = select(
            Feed.id,
            Feed.title,
            Feed.summary,
            Feed.published_date,
            Feed.view_count,
            Feed.organization_id,
            Organization.name.label('organization_name'),
            Feed.category_id,
            Category.name.label('category_name'),
            func.avg(Rating.score).label('average_rating')
        ).select_from(
            # 피드 테이블을 기준으로 JOIN 수행
            Feed.__table__.join(
                Organization.__table__, 
                Feed.organization_id == Organization.id
            ).join(
                Category.__table__,
                Feed.category_id == Category.id
            ).outerjoin(
                Rating.__table__, 
                Feed.id == Rating.feed_id
            )
        ).where(
            # 활성화된 피드만 조회
            Feed.is_active == True,
            # 특정 기관의 피드만 조회
            Organization.name == organization_name,
            # '보도자료' 카테고리 제외 (항상 적용)
            Category.name != '보도자료'
        )
        
        # category_id가 제공된 경우 해당 카테고리로 추가 필터링
        if category_id is not None:
            query = query.where(Feed.category_id == category_id)
        
        query = query.group_by(
            # 평균 별점 계산을 위한 그룹화
            Feed.id,
            Feed.title,
            Feed.summary,
            Feed.published_date,
            Feed.view_count,
            Feed.organization_id,
            Organization.name,
            Feed.category_id,
            Category.name
        ).order_by(
            # 발행일 기준 최신순 정렬
            Feed.published_date.desc()
        )
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'summary': row.summary,
                'published_date': row.published_date,
                'view_count': row.view_count,
                'organization_id': row.organization_id,
                'organization_name': row.organization_name,
                'category_id': row.category_id,
                'category_name': row.category_name,
                'average_rating': float(row.average_rating) if row.average_rating is not None else None
            }
            feeds_data.append(feed_dict)
        
        return feeds_data