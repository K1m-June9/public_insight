import asyncio
import logging

from typing import List, Dict, Tuple, Any
from sqlalchemy import select, update, func, case, or_, and_, desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BooleanClauseList
from elasticsearch import AsyncElasticsearch 
from datetime import datetime, timedelta

from app.F7_models.users import User
from app.F7_models.feeds import Feed
from app.F7_models.organizations import Organization
from app.F7_models.sliders import Slider
from app.F7_models.notices import Notice
from app.F7_models.bookmarks import Bookmark
from app.F7_models.ratings import Rating

# --- 로그 관련 테이블 ➡️ 엘라스틱 서치로 대체 ---
from app.F7_models.search_logs import SearchLog
from app.F7_models.user_activities import UserActivity

from app.F8_database.session import get_standalone_session

class DashboardAdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_overview_stats(self) -> Dict[str, int]:
        async with get_standalone_session() as db:
            """기본적인 개요 통계(총 사용자, 피드 수 등)를 한번의 쿼리로 조회"""
            today = datetime.utcnow().date()

            # --- 1. 사용자 관련 통계 조회 ---
            user_counts_stmt = select(
                func.count(User.id),
                func.sum(case((User.status == 'ACTIVE', 1), else_=0)),
                func.sum(case((func.date(User.created_at) == today, 1), else_=0))
            )

            user_result = await db.execute(user_counts_stmt)
            total_users, active_users, today_signups = user_result.one()
            
            
            # --- 2. 피드 관련 통계 조회 ---
            feed_counts_stmt = select(
                func.count(Feed.id),
                func.sum(Feed.view_count)
            )

            feed_result = await db.execute(feed_counts_stmt)
            total_feeds, total_views = feed_result.one()


            # --- 3. 기관 관련 통계 조회 ---
            total_orgs = await db.scalar(select(func.count(Organization.id)))

        # --- 4. 최종 결과 조합 ---
        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "today_signups": today_signups or 0,
            "total_feeds": total_feeds or 0,
            "total_organizations": total_orgs or 0,
            "total_views": int(total_views) if total_views else 0,
        }
    
    async def get_monthly_signups(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """최근 90일간의 일별 가입자 수를 조회"""
            ninety_days_ago = datetime.utcnow().date() - timedelta(days=90)

            stmt = select(
                func.date(User.created_at).label('date'),
                func.count(User.id).label('count')
            ).where(User.created_at >= ninety_days_ago).group_by('date').order_by('date')

            result = await db.execute(stmt)
            return [{"date":row.date, "count":row.count} for row in result.all()]
    
    async def get_organization_stats(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """가장 많은 피드를 보유한 기관 상위 5개를 조회"""
            stmt = select(
                Organization.name.label("organization_name"),
                func.count(Feed.id).label("feed_count")
            ).join(Feed, Organization.id == Feed.organization_id).group_by(Organization.name).order_by(desc("feed_count")).limit(5)
            
            result = await db.execute(stmt)
            return [{"organization_name": row.organization_name, "feed_count": row.feed_count} for row in result.all()]

    async def get_slider_stats(self) -> Dict[str, int]:
        async with get_standalone_session() as db:
            """활성/비활성 슬라이더의 개수를 조회"""
            stmt = select(
                func.sum(case((Slider.is_active == True, 1), else_=0)),
                func.sum(case((Slider.is_active == False, 1), else_=0))
            )

            active, inactive = (await db.execute(stmt)).one()
            return {"active": active or 0, "inactive": inactive or 0}
    
    async def get_notice_stats(self) -> Dict[str, int]:
        async with get_standalone_session() as db:
            """활성/비활성/고정 공지사항의 개수를 조회"""
            stmt = select(
                func.sum(case((Notice.is_active == True, 1), else_=0)),
                func.sum(case((Notice.is_active == False, 1), else_=0)),
                func.sum(case((Notice.is_pinned == True, 1), else_=0))
            )

            active, inactive, pinned = (await db.execute(stmt)).one()
            return {"active": active or 0, "inactive": inactive or 0, "pinned": pinned or 0}
    
    async def get_top_bookmarked_feeds(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """북마크가 가장 많이 된 피드 상위 3개를 조회"""
            # --- 서브쿼리를 사용하여 북마크 수를 계산 ---
            sub_stmt = select(
                Bookmark.feed_id,
                func.count(Bookmark.id).label('bookmark_count')
            ).group_by(Bookmark.feed_id).order_by(desc('bookmark_count')).limit(3).subquery()

            # --- 메인 쿼리에서 피드 및 기관 정보 조인 ---
            stmt = select(
                Feed.id, Feed.title,
                Organization.name.label("organization_name"), sub_stmt.c.bookmark_count
            ).join(sub_stmt, Feed.id == sub_stmt.c.feed_id).join(Organization, Feed.organization_id == Organization.id)
            
            result = await db.execute(stmt)
            return [dict(row) for row in result.mappings()]

    async def get_top_rated_feeds(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """평균 평점이 가장 높은 피드 상위 3개를 조회합니다."""
            sub_stmt = select(
                Rating.feed_id,
                func.avg(Rating.score).label('average_rating'),
                func.count(Rating.id).label('rating_count')
            ).group_by(Rating.feed_id).order_by(desc('average_rating'), desc('rating_count')).limit(3).subquery()
            
            stmt = select(
                Feed.id, Feed.title, Organization.name.label("organization_name"), sub_stmt.c.average_rating, sub_stmt.c.rating_count
            ).join(sub_stmt, Feed.id == sub_stmt.c.feed_id).join(Organization, Feed.organization_id == Organization.id)

            result = await db.execute(stmt)
            return [dict(row) for row in result.mappings()]
    
    # --- 로그 관련 DB ---

    async def get_recent_activities(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """가장 최근의 사용자 활동 로그 10개를 조회합니다."""
            query = select(
                UserActivity.id,
                UserActivity.activity_type.label("activity_type"),
                User.nickname.label("user_name"),
                UserActivity.target_id.label("target_id"),
                UserActivity.created_at.label("created_at")
            ).join(User, UserActivity.user_id == User.id).order_by(desc(UserActivity.created_at)).limit(10)
            
            result = await db.execute(query)
            return [dict(row) for row in result.mappings()]
    

    async def get_popular_keywords(self) -> List[Dict[str, Any]]:
        async with get_standalone_session() as db:
            """가장 많이 검색된 키워드 상위 5개를 조회합니다."""
            query = select(
                SearchLog.keyword,
                func.count(SearchLog.keyword).label('count')
            ).group_by(SearchLog.keyword).order_by(desc('count')).limit(5)
            result = await db.execute(query)
            return [{"keyword": row.keyword, "count": row.count} for row in result.all()]
        
