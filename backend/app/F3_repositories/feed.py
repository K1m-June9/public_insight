from sqlalchemy import select, func, and_, update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
import logging
from app.F7_models.feeds import Feed
from app.F7_models.ratings import Rating
from app.F7_models.organizations import Organization
from app.F7_models.categories import Category
from app.F7_models.bookmarks import Bookmark
from app.F7_models.users import User

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
    
    # 기관별 최신 피드 목록 조회 메서드
    # 입력: 
    #   limit - 최대 기관 수 제한 (int)
    # 반환: 
    #   기관별 최신 피드 정보가 포함된 Dict 객체들의 리스트 또는 None
    #   각 Dict는 피드 기본 정보와 기관 정보를 포함
    # 설명: 
    #   각 활성화된 기관의 가장 최신 피드를 기관당 1개씩 조회
    #   ROW_NUMBER()를 사용하여 기관별로 최신 피드만 선택
    #   published_date 기준 내림차순, 동일 시 created_at 기준 내림차순 정렬
    #   활성화된 피드(is_active=True)와 기관(is_active=True)만 대상
    #   결과가 없는 경우 None 반환
    async def get_latest_feeds_by_organization(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        # ROW_NUMBER()를 사용한 서브쿼리 구성
        # 각 기관별로 최신 피드 순위 매기기
        subquery = select(
            Feed.id,
            Feed.title,
            Feed.organization_id,
            Feed.published_date,
            Feed.created_at,
            func.row_number().over(
                partition_by=Feed.organization_id,
                order_by=[Feed.published_date.desc(), Feed.created_at.desc()]
            ).label('rn')
        ).where(
            # 활성화된 피드만 대상
            Feed.is_active == True
        ).subquery()
        
        # 메인 쿼리: 각 기관의 최신 피드(rn=1)와 기관 정보 JOIN
        query = select(
            subquery.c.id,
            subquery.c.title,
            subquery.c.organization_id,
            Organization.name.label('organization_name')
        ).select_from(
            # 서브쿼리와 기관 테이블 JOIN
            subquery.join(
                Organization.__table__,
                subquery.c.organization_id == Organization.id
            )
        ).where(
            # 각 기관의 최신 피드만 선택 (순위 1번)
            subquery.c.rn == 1,
            # 활성화된 기관만 대상
            Organization.is_active == True
        ).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'organization_id': row.organization_id,
                'organization_name': row.organization_name
            }
            feeds_data.append(feed_dict)
        
        return feeds_data
    
    # 기관별 카테고리별 최신 피드 목록 조회 메서드
    # 입력: 
    #   organization_name - 기관명 (str)
    #   limit - 최대 카테고리 수 제한 (int)
    # 반환: 
    #   기관 정보와 카테고리별 최신 피드 정보가 포함된 Dict 객체 또는 None
    #   기관 정보와 피드 리스트를 분리한 구조로 반환
    # 설명: 
    #   특정 기관의 각 카테고리별 가장 최신 피드를 카테고리당 1개씩 조회
    #   '보도자료' 카테고리는 제외하고 조회
    #   ROW_NUMBER()를 사용하여 카테고리별로 최신 피드만 선택
    #   published_date 기준 내림차순, 동일 시 created_at 기준 내림차순 정렬
    #   활성화된 피드(is_active=True)만 대상
    #   결과가 없는 경우 None 반환
    async def get_organization_latest_feeds_by_category(
        self, organization_name: str, limit: int
    ) -> Optional[Dict[str, Any]]:
        # ROW_NUMBER()를 사용한 서브쿼리 구성
        # 각 카테고리별로 최신 피드 순위 매기기
        subquery = select(
            Feed.id,
            Feed.title,
            Feed.category_id,
            Feed.organization_id,
            Feed.published_date,
            Feed.created_at,
            func.row_number().over(
                partition_by=Feed.category_id,
                order_by=[Feed.published_date.desc(), Feed.created_at.desc()]
            ).label('rn')
        ).select_from(
            Feed.__table__.join(
                Organization.__table__,
                Feed.organization_id == Organization.id
            ).join(
                Category.__table__,
                Feed.category_id == Category.id
            )
        ).where(
            # 특정 기관명으로 필터링
            Organization.name == organization_name,
            # 활성화된 피드만 대상
            Feed.is_active == True,
            # '보도자료' 카테고리 제외
            Category.name != '보도자료'
        ).subquery()
        
        # 메인 쿼리: 각 카테고리의 최신 피드(rn=1)와 기관, 카테고리 정보 JOIN
        query = select(
            subquery.c.id,
            subquery.c.title,
            subquery.c.category_id,
            subquery.c.organization_id,
            Organization.name.label('organization_name'),
            Category.name.label('category_name')
        ).select_from(
            subquery.join(
                Organization.__table__,
                subquery.c.organization_id == Organization.id
            ).join(
                Category.__table__,
                subquery.c.category_id == Category.id
            )
        ).where(
            # 각 카테고리의 최신 피드만 선택 (순위 1번)
            subquery.c.rn == 1
        ).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 첫 번째 행에서 기관 정보 추출
        first_row = rows[0]
        organization_info = {
            'id': first_row.organization_id,
            'name': first_row.organization_name
        }
        
        # 피드 리스트 구성
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'category_id': row.category_id,
                'category_name': row.category_name
            }
            feeds_data.append(feed_dict)
        
        # 기관 정보와 피드 리스트를 분리한 구조로 반환
        return {
            'organization': organization_info,
            'feeds': feeds_data
        }
    
    # 조회수 기준 상위 피드 목록 조회 메서드
    # 입력: 
    #   limit - 조회할 피드 수 제한 (int)
    # 반환: 
    #   조회수 기준 상위 피드 정보가 포함된 Dict 객체들의 리스트 또는 None
    #   각 Dict는 피드 기본 정보, 평균 별점, 조회수, 북마크 수를 포함
    # 설명: 
    #   활성화된 피드 중 조회수가 높은 순으로 정렬하여 상위 피드 조회
    #   동일 조회수일 경우 피드 ID가 큰 순으로 정렬
    #   결과가 없는 경우 None 반환
    async def get_top5_viewed(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        query = select(
            Feed.id,
            Feed.title,
            Feed.view_count,
            func.avg(Rating.score).label('average_rating'),
            func.count(Bookmark.id).label('bookmark_count')
        ).select_from(
            Feed.__table__.outerjoin(
                Rating.__table__,
                Feed.id == Rating.feed_id
            ).outerjoin(
                Bookmark.__table__,
                Feed.id == Bookmark.feed_id
            )
        ).where(
            Feed.is_active == True
        ).group_by(
            Feed.id, Feed.title, Feed.view_count
        ).order_by(
            Feed.view_count.desc(),
            Feed.id.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'average_rating': float(row.average_rating) if row.average_rating else 0.0,
                'view_count': row.view_count,
                'bookmark_count': row.bookmark_count
            }
            feeds_data.append(feed_dict)
        
        return feeds_data

    # 평균 별점 기준 상위 피드 목록 조회 메서드
    # 입력: 
    #   limit - 조회할 피드 수 제한 (int)
    # 반환: 
    #   평균 별점 기준 상위 피드 정보가 포함된 Dict 객체들의 리스트 또는 None
    #   각 Dict는 피드 기본 정보, 평균 별점, 조회수, 북마크 수를 포함
    # 설명: 
    #   활성화된 피드 중 평균 별점이 높은 순으로 정렬하여 상위 피드 조회
    #   별점이 없는 피드는 제외하고 조회 (INNER JOIN 사용)
    #   동일 평균 별점일 경우 피드 ID가 큰 순으로 정렬
    #   결과가 없는 경우 None 반환
    async def get_top5_rated(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        query = select(
            Feed.id,
            Feed.title,
            Feed.view_count,
            func.avg(Rating.score).label('average_rating'),
            func.count(Bookmark.id).label('bookmark_count')
        ).select_from(
            Feed.__table__.join(
                Rating.__table__,
                Feed.id == Rating.feed_id
            ).outerjoin(
                Bookmark.__table__,
                Feed.id == Bookmark.feed_id
            )
        ).where(
            Feed.is_active == True
        ).group_by(
            Feed.id, Feed.title, Feed.view_count
        ).order_by(
            func.avg(Rating.score).desc(),
            Feed.id.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'average_rating': float(row.average_rating),
                'view_count': row.view_count,
                'bookmark_count': row.bookmark_count
            }
            feeds_data.append(feed_dict)
        
        return feeds_data

    # 북마크 수 기준 상위 피드 목록 조회 메서드
    # 입력: 
    #   limit - 조회할 피드 수 제한 (int)
    # 반환: 
    #   북마크 수 기준 상위 피드 정보가 포함된 Dict 객체들의 리스트 또는 None
    #   각 Dict는 피드 기본 정보, 평균 별점, 조회수, 북마크 수를 포함
    # 설명: 
    #   활성화된 피드 중 북마크 수가 많은 순으로 정렬하여 상위 피드 조회
    #   북마크가 없는 피드는 제외하고 조회 (INNER JOIN 사용)
    #   동일 북마크 수일 경우 피드 ID가 큰 순으로 정렬
    #   결과가 없는 경우 None 반환
    async def get_top5_bookmarked(self, limit: int) -> Optional[List[Dict[str, Any]]]:
        query = select(
            Feed.id,
            Feed.title,
            Feed.view_count,
            func.avg(Rating.score).label('average_rating'),
            func.count(Bookmark.id).label('bookmark_count')
        ).select_from(
            Feed.__table__.join(
                Bookmark.__table__,
                Feed.id == Bookmark.feed_id
            ).outerjoin(
                Rating.__table__,
                Feed.id == Rating.feed_id
            )
        ).where(
            Feed.is_active == True
        ).group_by(
            Feed.id, Feed.title, Feed.view_count
        ).order_by(
            func.count(Bookmark.id).desc(),
            Feed.id.desc()
        ).limit(limit)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 쿼리 결과를 Dict 형태로 변환하여 반환
        feeds_data = []
        for row in rows:
            feed_dict = {
                'id': row.id,
                'title': row.title,
                'average_rating': float(row.average_rating) if row.average_rating else 0.0,
                'view_count': row.view_count,
                'bookmark_count': row.bookmark_count
            }
            feeds_data.append(feed_dict)
        
        return feeds_data
    
    # 기관별 보도자료 목록 조회 메서드 (페이지네이션)
    # 입력: 
    #   organization_name - 기관명 (str)
    #   offset - 시작 위치 (int)
    #   limit - 조회할 피드 수 제한 (int)
    # 반환: 
    #   기관 정보와 보도자료 목록이 포함된 Dict 객체 또는 None
    #   다음 페이지 존재 여부(has_more) 포함
    # 설명: 
    #   특정 기관의 '보도자료' 카테고리 피드만 조회
    #   published_date 기준 내림차순, 동일 시 created_at 기준 내림차순 정렬
    #   활성화된 피드(is_active=True)만 대상
    #   limit + 1개 조회하여 다음 페이지 존재 여부 확인
    #   결과가 없는 경우 None 반환
    async def get_organization_press(
        self, organization_name: str, offset: int, limit: int
    ) -> Optional[Dict[str, Any]]:
        # 메인 쿼리: 기관의 보도자료 조회 (평균 별점 포함)
        query = select(
            Feed.id,
            Feed.title,
            Feed.summary,
            Feed.published_date,
            Feed.view_count,
            Feed.organization_id,
            Organization.name.label('organization_name'),
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.avg(Rating.score).label('average_rating')
        ).select_from(
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
            # 특정 기관명으로 필터링
            Organization.name == organization_name,
            # '보도자료' 카테고리만 필터링
            Category.name == '보도자료',
            # 활성화된 피드만 대상
            Feed.is_active == True
        ).group_by(
            Feed.id, Feed.title, Feed.summary, Feed.view_count, Feed.published_date,
            Feed.organization_id, Organization.name,
            Category.id, Category.name
        ).order_by(
            Feed.published_date.desc(),
            Feed.created_at.desc()
        ).offset(offset).limit(limit + 1)  # limit + 1개 조회 (다음 페이지 확인용)
        
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        # 결과가 없는 경우 None 반환
        if not rows:
            return None
        
        # 다음 페이지 존재 여부 확인
        has_more = len(rows) > limit
        actual_rows = rows[:limit]  # 실제 반환할 데이터 (limit개만)
        
        # 첫 번째 행에서 기관 정보 추출
        first_row = actual_rows[0]
        organization_info = {
            'id': first_row.organization_id,
            'name': first_row.organization_name
        }
        
        # 보도자료 리스트 구성
        press_releases_data = []
        for row in actual_rows:
            press_release_dict = {
                'id': row.id,
                'title': row.title,
                'summary': row.summary,
                'published_date': row.published_date,
                'view_count': row.view_count,
                'average_rating': float(row.average_rating) if row.average_rating else 0.0,
                'category_id': row.category_id,
                'category_name': row.category_name
            }
            press_releases_data.append(press_release_dict)
        
        # 기관 정보, 보도자료 리스트, 다음 페이지 여부를 포함한 구조로 반환
        return {
            'organization': organization_info,
            'press_releases': press_releases_data,
            'has_more': has_more
        }
    
    # 특정 피드의 상세 정보 조회 메서드
    # 입력: 
    #   feed_id - 조회할 피드 ID (int)
    # 반환: 
    #   피드 상세 정보가 포함된 Dict 객체 또는 None
    #   Dict는 피드 기본 정보, 평균 별점, 기관/카테고리 정보를 포함
    # 설명: 
    #   활성화된 피드, 기관, 카테고리만 조회 (3중 활성화 체크)
    #   Rating 테이블과 LEFT JOIN하여 평균 별점 계산
    #   original_text를 content로 반환 -> 삭제
    #   {pdf_file_path 반환}
    #   결과가 없는 경우 None 반환

    # async def get_feed_detail(self, feed_id: int) -> Optional[Dict[str, Any]]:
    #     try:
    #         # 서브쿼리: 피드별 평균 별점 계산
    #         rating_subquery = (
    #             self.db.query(
    #                 Rating.feed_id,
    #                 func.avg(Rating.score).label('average_rating')
    #             )
    #             .group_by(Rating.feed_id)
    #             .subquery()
    #         )
            
    #         # 메인 쿼리: 피드 상세 정보 조회
    #         query = (
    #             self.db.query(
    #                 Feed.id,
    #                 Feed.title,
    #                 #Feed.original_text.label('content'),
    #                 Feed.source_url,
    #                 Feed.pdf_file_path,
    #                 Feed.published_date,
    #                 Feed.view_count,
    #                 Organization.id.label('organization_id'),
    #                 Organization.name.label('organization_name'),
    #                 Category.id.label('category_id'),
    #                 Category.name.label('category_name'),
    #                 rating_subquery.c.average_rating
    #             )
    #             .join(Organization, Feed.organization_id == Organization.id)
    #             .join(Category, Feed.category_id == Category.id)
    #             .outerjoin(rating_subquery, Feed.id == rating_subquery.c.feed_id)
    #             .filter(
    #                 and_(
    #                     Feed.id == feed_id,
    #                     Feed.is_active == True
    #                 )
    #             )
    #         )
            
    #         result = query.first()
            
    #         if not result:
    #             return None
                
    #         return {
    #             'id': result.id,
    #             'title': result.title,
    #             #'content': result.content,
    #             'source_url': result.source_url,
    #             'pdf_file_path': result.pdf_file_path,
    #             'published_date': result.published_date,
    #             'view_count': result.view_count,
    #             'average_rating': float(result.average_rating) if result.average_rating else 0.0,
    #             'organization_id': result.organization_id,
    #             'organization_name': result.organization_name,
    #             'category_id': result.category_id,
    #             'category_name': result.category_name
    #         }
            
    #     except Exception as e:
    #         logger.error(f"피드 상세 조회 중 오류 발생 - feed_id: {feed_id}, error: {str(e)}")
    #         return None

    async def get_feed_detail(self, feed_id: int) -> Optional[Dict[str, Any]]:
        """
        특정 피드의 상세 정보를 비동기적으로 조회합니다.
        self.db는 AsyncSession 객체여야 합니다.
        """
        try:
            # 서브쿼리: 피드별 평균 별점 계산 (select 구문 사용)
            rating_subquery = (
                select(
                    Rating.feed_id,
                    func.avg(Rating.score).label('average_rating')
                )
                .group_by(Rating.feed_id)
                .subquery()
            )
        
            # 메인 쿼리: 피드 상세 정보 조회 (select 구문 사용)
            query = (
                select(
                    Feed.id,
                    Feed.title,
                    Feed.source_url,
                    Feed.pdf_file_path,
                    Feed.published_date,
                    Feed.view_count,
                    Organization.id.label('organization_id'),
                    Organization.name.label('organization_name'),
                    Category.id.label('category_id'),
                    Category.name.label('category_name'),
                    rating_subquery.c.average_rating
                )
                .join(Organization, Feed.organization_id == Organization.id)
                .join(Category, Feed.category_id == Category.id)
                .outerjoin(rating_subquery, Feed.id == rating_subquery.c.feed_id)
                .where(
                    and_(
                        Feed.id == feed_id,
                        Feed.is_active == True,
                        Organization.is_active == True,  # 기관 활성화 체크 추가
                        Category.is_active == True      # 카테고리 활성화 체크 추가
                    )
                )
            )
        
            # 쿼리를 비동기적으로 실행
            result = await self.db.execute(query)
            # 첫 번째 결과 레코드를 가져옴
            record = result.first()
        
            if not record:
                return None
            
            return {
                'id': record.id,
                'title': record.title,
                'source_url': record.source_url,
                'pdf_file_path': record.pdf_file_path,
                'published_date': record.published_date,
                'view_count': record.view_count,
                'average_rating': float(record.average_rating) if record.average_rating else 0.0,
                'organization_id': record.organization_id,
                'organization_name': record.organization_name,
                'category_id': record.category_id,
                'category_name': record.category_name
            }
        
        except Exception as e:
            logger.error(f"피드 상세 조회 중 오류 발생 - feed_id: {feed_id}, error: {str(e)}")
            return None


    # 특정 피드의 조회수 증가 메서드
    # 입력: 
    #   feed_id - 조회수를 증가시킬 피드 ID (int)
    # 반환: 
    #   성공 여부 (bool)
    # 설명: 
    #   활성화된 피드의 조회수를 1 증가시킴
    #   피드가 존재하지 않거나 비활성화된 경우 False 반환
    #   예외 발생 시 롤백 후 False 반환

    # async def increment_feed_view_count(self, feed_id: int) -> bool:
    #     try:
    #         result = (
    #             self.db.query(Feed)
    #             .filter(
    #                 and_(
    #                     Feed.id == feed_id,
    #                     Feed.is_active == True
    #                 )
    #             )
    #             .update(
    #                 {Feed.view_count: Feed.view_count + 1},
    #                 synchronize_session=False
    #             )
    #         )
            
    #         if result > 0:
    #             self.db.commit()
    #             logger.info(f"피드 조회수 증가 성공 - feed_id: {feed_id}")
    #             return True
    #         else:
    #             logger.warning(f"피드 조회수 증가 실패 - 피드를 찾을 수 없음: feed_id: {feed_id}")
    #             return False
                
    #     except Exception as e:
    #         self.db.rollback()
    #         logger.warning(f"피드 조회수 증가 중 오류 발생 - feed_id: {feed_id}, error: {str(e)}")
    #         return False
    

    async def increment_feed_view_count(self, feed_id: int) -> bool:
        """
        피드의 조회수를 1 증가시킵니다. (비동기 방식)
        """
        try:
            # 1. 비동기용 UPDATE 구문(Statement) 생성
            stmt = (
                update(Feed)
                .where(
                    and_(
                        Feed.id == feed_id,
                        Feed.is_active == True
                    )
                )
                .values(view_count=Feed.view_count + 1)
            )

            # 2. 생성된 구문을 비동기 세션으로 실행
            result = await self.db.execute(stmt)

            # 3. 실제로 업데이트된 행(row)의 수를 확인
            if result.rowcount > 0:
                # 4. 성공 시 비동기로 commit
                await self.db.commit()
                logger.info(f"피드 조회수 증가 성공 - feed_id: {feed_id}")
                return True
            else:
                # 업데이트된 행이 없으면, 해당 ID의 활성 피드가 없다는 의미
                logger.warning(f"피드 조회수 증가 실패 - 피드를 찾을 수 없음: feed_id: {feed_id}")
                return False
                
        except Exception as e:
            # 5. 예외 발생 시 비동기로 rollback
            await self.db.rollback()
            logger.error(f"피드 조회수 증가 중 DB 오류 발생 - feed_id: {feed_id}, error: {str(e)}")
            return False


    async def is_feed_exists(self, feed_id: int) -> bool:
        result = await self.db.execute(
            select(Feed).where(Feed.id == feed_id, Feed.is_active.is_(True))
        )
        feed = result.scalars().first()
        return feed is not None

    async def is_rating_exists(self, feed_id: int, user_pk: int) -> bool:
        result = await self.db.execute(
            select(Rating).where(
                    Rating.feed_id == feed_id,
                    Rating.user_id == user_pk    
            )
        )
        rating = result.scalars().first()
        return rating is not None

    async def get_user_pk_by_user_id(self, user_id: str) -> int | None:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        
        user_obj = result.scalar_one_or_none()
        if user_obj is None:
            return None
        return user_obj.id

    async def register_rating(self, feed_id: int, user_pk: int, score: int) -> None:
        new_rating = Rating(
            feed_id=feed_id, 
            user_id=user_pk, 
            score=score
        )

        self.db.add(new_rating)
        await self.db.commit()
        await self.db.refresh(new_rating)

    async def get_feed_rating(self, feed_id: int) -> dict:
        result = await self.db.execute(
            select(
                func.avg(Rating.score).label("average_rating"),
                func.count(Rating.id).label("total_ratings")
            ).where(Rating.feed_id == feed_id)
        )
        row = result.first()
        if row is None:
            return {"average_rating": 0.0, "total_ratings": 0}

        average_rating, total_ratings = row
        return {
            "average_rating": float(average_rating or 0),
            "total_ratings": total_ratings
        }
    

    async def get_bookmark(self, user_pk: int, feed_id: int) -> Bookmark | None:
        result = await self.db.execute(
            select(Bookmark).where(
                Bookmark.user_id == user_pk,
                Bookmark.feed_id == feed_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create_bookmark(self, user_pk: int, feed_id: int):
        new_bookmark = Bookmark(user_id=user_pk, feed_id=feed_id)
        self.db.add(new_bookmark)
        await self.db.commit()
        await self.db.refresh(new_bookmark)
    
    async def delete_bookmark(self, bookmark_id: int):
        bookmark = await self.db.get(Bookmark, bookmark_id)
        if bookmark:
            await self.db.delete(bookmark)
            await self.db.commit()

    
    async def get_bookmark_count(self, feed_id: int) -> int:
        result = await self.db.execute(
            select(func.count(Bookmark.id)).where(Bookmark.feed_id == feed_id)
        )
        return result.scalar_one()
    
    async def get_user_rating_for_feed(self, user_pk: int, feed_id: int) -> Optional[Rating]:
        """
        특정 사용자가 특정 피드에 남긴 별점(Rating) 객체를 조회
        피드 상세페이지에서 로그인된 사용자가 사용할 메서드
        is_rating_exists <- 쓰고싶었는데 T/F 반환이라서 못씀 ㅅㅂㅋㅋ
        
        Args:
            user_pk (int): 사용자 기본 키
            feed_id (int): 피드 ID
        
        Returns:
            Optional[Rating]: Rating 객체 또는 None
        """
        result = await self.db.execute(
            select(Rating).where(
                Rating.user_id == user_pk,
                Rating.feed_id == feed_id
            )
        )
        return result.scalar_one_or_none()