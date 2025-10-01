from typing import Union, Optional
from sqlalchemy.exc import SQLAlchemyError 
from pathlib import Path
from fastapi import UploadFile, BackgroundTasks

import uuid
import math
import logging
import asyncio
import base64
import os 

from app.F3_repositories.admin.dashboard import DashboardAdminRepository
from app.F3_repositories.admin.dashboard_activity import DashboardActivityRepository
from app.F5_core.config import settings

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

from app.F6_schemas.base import (
    ErrorResponse, 
    ErrorDetail, 
    ErrorCode, 
    Message, 
    Settings,
    PaginatedResponse, 
    PaginationQuery,
    PaginationInfo,
    UserRole,
)

from app.F6_schemas.admin.dashboard import (
    DashboardResponse,
    DashboardData,
)
logger = logging.getLogger(__name__)

class DashboardAdminService:
    def __init__(self, dash_repo: DashboardAdminRepository, es_repo:DashboardActivityRepository):
        self.dash_repo = dash_repo
        self.es_repo = es_repo


    async def get_dashboard_stats(self, current_user: User) -> Union[DashboardResponse, ErrorResponse]:
        try:

            # 2. 모든 비동기 작업을 리스트로 묶어 asyncio.gather로 동시에 실행
            tasks = [
                self.dash_repo.get_overview_stats(),
                self.dash_repo.get_monthly_signups(),
                self.dash_repo.get_organization_stats(),
                self.dash_repo.get_slider_stats(),
                self.dash_repo.get_notice_stats(),
                self.dash_repo.get_top_bookmarked_feeds(),
                self.dash_repo.get_top_rated_feeds(),
            ]

            # 환경에 따라 ES 관련 작업 추가
            if settings.ENVIRONMENT == "production":
                logger.info("Production environment detected. Including Elasticsearch stats.")
                tasks.append(self.es_repo.get_popular_keywords())
                tasks.append(self.es_repo.get_recent_activities())
            else:
                logger.info("Dev env: Skipping Elasticsearch stats.")

            # 3. 모든 작업이 완료될 때까지 기다리고 결과를 한 번에 받음
            results = await asyncio.gather(*tasks)

            # 4. 결과 언패킹 (순서가 보장됨)
            overview_stats, monthly_signups, organization_stats, slider_stats, notice_stats, top_bookmarked_feeds, top_rated_feeds = results[:7]
            
            if settings.ENVIRONMENT == "production":
                popular_keywords = results[7]
                recent_activities = results[8]
            else:
                popular_keywords = []
                recent_activities = []

            # --- 3. 성공 응답 반환 ---
            dashboard_data = DashboardData(
                **overview_stats,
                monthly_signups=monthly_signups,
                popular_keywords=popular_keywords,
                organization_stats=organization_stats,
                slider_stats=slider_stats,
                notice_stats=notice_stats,
                top_bookmarked_feeds=top_bookmarked_feeds,
                top_rated_feeds=top_rated_feeds,
                recent_activities=recent_activities,
            )
            
            # --- 4. 성공 응답 반환 ----
            return DashboardResponse(data=dashboard_data)
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_dashboard_stats service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_dashboard_stats service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        