from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
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

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    

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
