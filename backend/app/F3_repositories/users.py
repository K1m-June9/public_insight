from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, List, Any
import logging

from app.F6_schemas.users import (
    RatingItem, BookmarkItem
)
from app.F7_models.users import User
from app.F7_models.ratings import Rating
from app.F7_models.feeds import Feed
from app.F7_models.bookmarks import Bookmark
from app.F7_models.categories import Category
from app.F7_models.organizations import Organization
from app.F8_database.graph_db import Neo4jDriver

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.neo4j_driver = Neo4jDriver.get_driver()
    

    async def is_nickname_exists(self, nickname: str, exclude_user_id: str | None = None) -> bool:
        """nickname 중복 여부 확인"""
        stmt = select(User).where(User.nickname == nickname)
        if exclude_user_id:
            stmt = stmt.where(User.user_id != exclude_user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None


    async def update_nickname(self,user_id: str, new_nickname: str):
        """사용자의 닉네임 변경"""
        # user_id와 일치하는 사용자 조회
        result = await self.db.execute(
            select(User).where((User.user_id == user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")
        
        if user.nickname == new_nickname:
            return # 변경 없음
        
        user.nickname = new_nickname
        await self.db.commit()
        await self.db.refresh(user)
    

    # user_id(사용자 아이디)를 기준으로 User 객체를 DB에서 조회하는 함수
    # 입력: user_id
    # 반환: User 객체 또는 조회 실패 시 None
    async def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()
    

    async def update_password(self, user_id: str, password: str):
        """비밀번호 변경"""
        # 1. user_id로 사용자 조회
        result = await self.db.execute(
            select(User).where((User.user_id == user_id)))
        user = result.scalar_one_or_none()

        # 2. 사용자가 존재하지 않으면 예외 발생
        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")
        
        # 3. 비밀번호 해시 업데이트
        user.password_hash = password
        await self.db.commit()
        await self.db.refresh(user)


    async def get_user_pk_by_user_id(self, user_id: str) -> int | None:
        """주어진 user_id로 User 테이블에서 PK(id)를 조회"""
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        user_obj = result.scalar_one_or_none() # 결과가 없으면 None 반환
        return user_obj.id if user_obj else None
    

    async def get_total_ratings_count(self, user_pk: int) -> int:
        """특정 사용자가 남긴 별점의 총 개수를 반환"""
        result = await self.db.execute(
            select(func.count()) # 카운트 쿼리
            .select_from(Rating)
            .where(Rating.user_id == user_pk)
        )
        return result.scalar_one() # 총 개수 반환


    async def get_ratings_data(self, user_pk: int, offset: int, limit: int) -> list[RatingItem]:
        """
        사용자가 남긴 별점과 관련 피드 정보를 조회
        (pagination 적용: offset, limit)
        """
        stmt = (
            select(
                Feed.id.label("feed_id"),       # 피드 ID
                Feed.title.label("feed_title"), # 피드 제목
                Feed.organization_id,           # 소속 기관 ID
                Organization.name.label("organization_name"),   # 소속 기관 이름
                Feed.category_id,               # 카테고리 ID
                Category.name.label("category_name"),           # 카테고리 이름
                Feed.view_count,                                # 피드 조회수
                Feed.published_date,                            # 원본 콘텐츠의 발행 일시
                Rating.score.label("user_rating"),              # 사용자가 준 별점
                func.avg(Rating.score).over(partition_by=Feed.id).label("average_rating"),                              # 해당 피드의 평균
                Rating.created_at.label("rated_at"),             # 사용자가 별점 남긴 날짜
            )
            .join(Rating, Rating.feed_id == Feed.id)    
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
            .where(
                Rating.user_id == user_pk,  # 해당 사용자의 별점만 조회
                Feed.is_active.is_(True)    # 활성화된 피드만
            )
            .order_by(Rating.created_at.desc()) # 최신 별점부터 정렬
            .offset(offset)                     # 페이지네이션: 시작 위치
            .limit(limit)                       # 페이지네이션: 조회 개수
        )

        result = await self.db.execute(stmt)
        rows = result.all() # 결과 전부 가져오기

        # SQLAlchemy Row 객체를 RatingItem으로 변환
        return [RatingItem(**dict(row._mapping)) for row in rows]


    async def get_total_bookmarks_count(self, user_pk: int) -> int:
        """특정 사용자가 남긴 별점의 총 개수를 반환"""
        result = await self.db.execute(
            select(func.count()) # 카운트 쿼리
            .select_from(Bookmark)
            .where(Bookmark.user_id == user_pk)
        )
        return result.scalar_one() # 총 개수 반환
    
    
    async def get_bookmarks_data(self, user_pk: int, offset: int, limit: int) -> list[BookmarkItem]:
        """
        북마크된 피드 정보를 조회
        (pagination 적용: offset, limit)
        """
        stmt = (
            select(
                Feed.id.label("feed_id"),       # 피드 ID
                Feed.title.label("feed_title"), # 피드 제목
                Feed.organization_id,           # 소속 기관 ID
                Organization.name.label("organization_name"),   # 소속 기관 이름
                Feed.category_id,               # 카테고리 ID
                Category.name.label("category_name"),           # 카테고리 이름
                Feed.view_count,                                # 피드 조회수
                Feed.published_date,                            # 원본 콘텐츠의 발행 일시
                Bookmark.created_at.label("bookmarked_at")
            )
            .join(Bookmark, Bookmark.feed_id == Feed.id)    
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
            .where(
                Bookmark.user_id == user_pk,  # 해당 사용자의 별점만 조회
                Feed.is_active.is_(True)    # 활성화된 피드만
            )
            .order_by(Bookmark.created_at.desc()) # 최신 북마크 순으로 정렬
            .offset(offset)                     # 페이지네이션: 시작 위치
            .limit(limit)                       # 페이지네이션: 조회 개수
        )

        result = await self.db.execute(stmt)
        rows = result.all() # 결과 전부 가져오기

        # SQLAlchemy Row 객체를 RatingItem으로 변환
        return [BookmarkItem(**dict(row._mapping)) for row in rows]
    
    async def get_latest_user_activities(self, user_pk: int, limit: int = 5) -> List[int]:
        """
        [MySQL] 사용자의 가장 최근 활동(북마크, 4점 이상 별점)에 해당하는 피드 ID를 조회.
        - 추천의 '씨앗' 데이터를 수집하는 첫 단계임.
        """
        # 북마크 서브쿼리
        bookmark_sq = (
            select(Bookmark.feed_id, Bookmark.created_at.label("activity_at"))
            .where(Bookmark.user_id == user_pk)
        )
        # 긍정적 별점 서브쿼리
        rating_sq = (
            select(Rating.feed_id, Rating.created_at.label("activity_at"))
            .where(Rating.user_id == user_pk, Rating.score >= 4)
        )
        # 두 활동을 합치고, 최신순으로 정렬하여 피드 ID만 가져옴
        union_stmt = bookmark_sq.union_all(rating_sq)
        final_stmt = (
            select(union_stmt.c.feed_id)
            .order_by(union_stmt.c.activity_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(final_stmt)
        # [123, 456, ...] 형태의 피드 ID 리스트를 반환
        return result.scalars().all()

    async def get_user_searched_keywords(self, user_pk: int, limit: int = 5) -> List[str]:
        """
        [Neo4j] 사용자가 과거에 검색했던 키워드를 최신순으로 조회.
        - 추천의 '씨앗' 데이터를 수집하는 두 번째 단계임.
        """
        cypher_query = """
        MATCH (u:User {id: $user_pk})-[r:SEARCHED]->(k:Keyword)
        RETURN k.id AS keyword
        // --- ▼ [수정] elementId()는 Neo4j 5.x 이상 버전 함수이므로, 4.4 버전에 맞는 id()로 변경합니다. ▼ ---
        // id(r)은 관계의 내부 ID를 반환하므로, 최신순을 근사적으로 정렬하는 데 동일하게 사용할 수 있습니다.
        ORDER BY id(r) DESC 
        LIMIT $limit
        """
        try:
            async with self.neo4j_driver.session() as session:
                result = await session.run(cypher_query, user_pk=user_pk, limit=limit)
                return [record["keyword"] async for record in result]
        except Exception as e:
            logger.error(f"Neo4j에서 사용자 검색 키워드 조회 실패 (user_pk: {user_pk}): {e}", exc_info=True)
            return []

    async def get_popular_feeds_for_fallback(self, limit: int = 5) -> List[int]:
        """
        [Neo4j] 폴백 추천을 위한 가장 인기 있는 피드 ID를 조회.
        - 4점 이상 별점은 1.5점, 북마크는 1.0점으로 가중치를 두어 합산 점수가 높은 순으로 정렬.
        """
        cypher_query = """
        MATCH (f:Feed)
        OPTIONAL MATCH (f)<-[r_rating:RATED_POSITIVELY]-(:User)
        OPTIONAL MATCH (f)<-[r_bookmark:BOOKMARKED]-(:User)
        WITH f, 
             count(r_rating) AS positive_ratings, 
             count(r_bookmark) AS bookmarks
        WHERE positive_ratings > 0 OR bookmarks > 0
        RETURN f.id AS feedId, 
               (positive_ratings * 1.5) + (bookmarks * 1.0) AS popularityScore
        ORDER BY popularityScore DESC, f.id DESC
        LIMIT $limit
        """
        try:
            async with self.neo4j_driver.session() as session:
                result = await session.run(cypher_query, limit=limit)
                return [record["feedId"] async for record in result]
        except Exception as e:
            logger.error(f"Neo4j에서 인기 피드 조회 실패: {e}", exc_info=True)
            return []
        

    async def get_rich_feed_details_by_ids(self, feed_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """
        [MySQL] 주어진 feed_id 리스트에 해당하는 피드들의 모든 상세 정보를 일괄 조회.
        - 추천 데이터 '보강(Enrichment)'을 위한 핵심 메서드임.
        - 단 한 번의 쿼리로 N개의 피드 정보를 모두 가져와 N+1 문제를 방지함.
        """
        if not feed_ids:
            return {}

        # 피드별 평균 별점과 북마크 수를 계산하는 서브쿼리
        rating_sq = (
            select(
                Rating.feed_id,
                func.avg(Rating.score).label("average_rating")
            )
            .where(Rating.feed_id.in_(feed_ids))
            .group_by(Rating.feed_id)
            .subquery()
        )
        bookmark_sq = (
            select(
                Bookmark.feed_id,
                func.count(Bookmark.id).label("bookmark_count")
            )
            .where(Bookmark.feed_id.in_(feed_ids))
            .group_by(Bookmark.feed_id)
            .subquery()
        )

        # 메인 쿼리
        stmt = (
            select(
                Feed.id,
                Feed.title,
                Feed.summary,
                Feed.published_date,
                Feed.view_count,
                Organization.name.label("organization_name"),
                Category.name.label("category_name"),
                # 서브쿼리 결과가 없는 경우(NULL) 0으로 처리
                func.coalesce(rating_sq.c.average_rating, 0.0).label("average_rating"),
                func.coalesce(bookmark_sq.c.bookmark_count, 0).label("bookmark_count")
            )
            .select_from(Feed)
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
            .outerjoin(rating_sq, Feed.id == rating_sq.c.feed_id)
            .outerjoin(bookmark_sq, Feed.id == bookmark_sq.c.feed_id)
            .where(Feed.id.in_(feed_ids))
        )

        result = await self.db.execute(stmt)
        
        # 결과를 {feed_id: {상세정보}} 형태의 딕셔너리로 변환하여 반환
        return {row.id: dict(row._mapping) for row in result}