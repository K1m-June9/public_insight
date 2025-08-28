from typing import Union
from sqlalchemy.exc import SQLAlchemyError 
import math
import logging
import asyncio

from app.F3_repositories.admin.users import UsersAdminRepository
from app.F3_repositories.admin.activity_log import UsersActivityRepository 

from app.F6_schemas.admin.users import (
    UserListResponse,
    UserListRequest,
    UserListStatistics,
    UserRoleStats,
    UserRole,
    UserStatusStats,
    UserStatus,
    UserListItem,
    UserListData,
    UserDetailResponse,
    UserDetail,
    UserStatistics,
    UserActivityResponse,
    UserActivity,
    UserActivityData,
    UserRoleChangeResponse,
    UserRoleUpdate,
    UserStatusChangeResponse,
    UserStatusUpdate,

)
from app.F6_schemas.base import (
    ErrorResponse, 
    ErrorDetail, 
    ErrorCode, 
    Message, 
    Settings,
    PaginatedResponse, 
    PaginationQuery,
    PaginationInfo,
    
)

logger = logging.getLogger(__name__)

class UsersAdminService:
    def __init__(self, user_repo: UsersAdminRepository, activity_repo: UsersActivityRepository):
        self.user_repo = user_repo 
        self.activity_repo = activity_repo

    async def get_user_list(self, params: UserListRequest) -> Union[UserListResponse, ErrorResponse]:
        """페이지네이션, 검색, 필터링 기능이 포함된 사용자 목록을 조회"""
        try:
            # --- 1. 데이터 조회 ---
            total_users_count = await self.user_repo.get_total_user_count()  # 전체 사용자 수
            role_counts = await self.user_repo.get_user_counts_by_role()     # 역할별 수
            status_counts = await self.user_repo.get_user_counts_by_status() # 상태별 수
            
            # 응답 스키마에 맞게 통계 데이터 구성
            statistics = UserListStatistics(
                total_users=total_users_count,
                by_role = UserRoleStats(
                    admin=role_counts.get(UserRole.ADMIN, 0),
                    moderator=role_counts.get(UserRole.MODERATOR, 0),
                    user=role_counts.get(UserRole.USER, 0),
                ),
                by_status=UserStatusStats(
                    active=status_counts.get(UserStatus.ACTIVE, 0),
                    inactive=status_counts.get(UserStatus.INACTIVE, 0),
                    suspended=status_counts.get(UserStatus.SUSPENDED, 0),
                    deleted=status_counts.get(UserStatus.DELETED, 0),
                )
            )
        
            # 필터링 및 페이지네이션된 사용자 목록 조회
            paginated_users = await self.user_repo.get_paginated_user_list(params)

            # 필터링된 결과의 전체 개수 조회
            total_filtered_count = await self.user_repo.get_filtered_user_count(params)

            # --- 2. PaginationInfo 객체 생성(1단계) ---
            # 페이지네이션 정보 계산
            total_pages = math.ceil(total_filtered_count / params.limit) if total_filtered_count > 0 else 1
            
            pagination_info_obj = PaginationInfo(
                current_page=params.page,
                total_pages=total_pages,
                total_count=total_filtered_count,
                limit=50,
                has_next=params.page < total_pages,
                has_previous=params.page > 1
            )

            # # --- 3. PaginatedResponse 객체 생성(2단계) ---
            # paginated_response_for_field = PaginatedResponse(
            #     data = [],
            #     pagination=pagination_info_obj
            # )

            # --- 4. 최종 응답 데이터 구성 ---
            # 최종 응답 데이터 구성
            # 조회된 사용자 목록을 응답 스키마로 변환
            user_list_items = [UserListItem.model_validate(user, from_attributes=True) for user in paginated_users]
            # user_list_items = [UserListItem.from_orm(user) for user in paginated_users]


            response_data = UserListData(
                users=user_list_items,
                pagination=pagination_info_obj,
                statistics=statistics
            )
            # 최종 반환
            return UserListResponse(
                success = True,
                data = response_data
            )
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_user_list service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_user_list service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )




    async def get_user_detail(self, user_id: str) -> Union[UserDetailResponse, ErrorResponse]:
        try:
            # --- 1. 사용자 조회 ---
            user = await self.user_repo.get_user_by_id(user_id)

            # --- 2. 사용자가 없는 경우 Not Found 에러 반환 ---
            if not user:
                return ErrorResponse(
                    error = ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
                    )
                )
            
            # --- 3. 각 데이터 소스에서 통계 정보 비동기적으로 동시 조회 ---
            rdb_stats_task = self.user_repo.get_rdb_user_statistics(user_id)

            # ‼️ FIXME: 로직이 완전히 맞는지 확신 없음. 나중에 다시 검토 필요 ‼️
            es_stats_task = self.activity_repo.get_es_user_statistics(user_id)

            rdb_stats, es_stats = await asyncio.gather(rdb_stats_task, es_stats_task)

            # --- 4. 조합된 모든 통계 데이터 조합 ---
            total_activities = (
                rdb_stats.get("total_bookmarks", 0) +
                rdb_stats.get("total_ratings", 0) +
                es_stats.get("total_searches", 0)
            )
            
            # UserStatistics Pydantic 모델 생성
            stats_obj = UserStatistics(
                total_bookmarks=rdb_stats.get("total_bookmarks", 0),
                total_ratings=rdb_stats.get("total_ratings", 0),
                total_searches=es_stats.get("total_searches", 0),
                last_activity_at=es_stats.get("last_activity_at"),
                total_activities=total_activities
            )

            # --- 5. 최종 UserDetail 객체 생성 ---
            user_data_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            user_data_dict['statistics'] = stats_obj
            user_detail_data = UserDetail(**user_data_dict)

            return UserDetailResponse(
                success=True,
                data=user_detail_data
            )

        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_user_detail service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_user_detail service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def get_user_detail_log(self, user_id:str, page: int, limit: int) -> Union[UserActivityResponse, ErrorResponse]:
        try:
            # --- 1. 페이지네이션된 로그 데이터와 전체 개수 조회 ---
            total_count, logs = await self.activity_repo.get_paginated_activity_logs(user_id, page, limit)

            # --- 2. 페이지네이션 정보 계산 ---
            total_pages = math.ceil(total_count /limit) if total_count > 0 else 1

            pagination_info = PaginationInfo(
                current_page=page,
                total_pages=total_pages,
                total_count=total_count,
                limit=limit,
                has_next=page < total_pages,
                has_previous=page > 1
            )


            # --- 3. 최종 응답 데이터 ---
            activity_items = [UserActivity(**log) for log in logs]

            user_activity_data = UserActivityData(
                activities=activity_items,
                pagination=pagination_info
            )

            return UserActivityResponse(
                success=True,
                data=user_activity_data
            )
        
        except Exception as e:
            logger.error(f"Error in Admin get_user_detail_log service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def update_user_role(self, user_id:str, new_role:UserRole) -> Union[UserRoleChangeResponse, ErrorResponse]:
        try:
            # --- 1. 사용자 조회 ---
            user = await self.user_repo.get_user_by_id(user_id)

            # --- 2. 사용자가 없는 경우 Not Found 에러 반환 ---
            if not user:
                return ErrorResponse(
                    error = ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
                    )
                )
            
            # --- 3. 비즈니스 규칙 검증 ---
            # ADMIN 역할은 변경 x
            if user.role == UserRole.ADMIN:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.FORBIDDEN,
                        message=Message.FORBIDDEN
                    )
                )
            
            # 부여 가능한 역할은 USER 또는 MODERATOR 뿐임
            if new_role not in [UserRole.USER, UserRole.MODERATOR ]:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INVALID_PARAMETER,
                        message=Message.INVALID_PARAMETER
                    )
                )
            
            # --- 4. 리포지토리를 통해 역할 업데이트 ---
            update_user = await self.user_repo.update_user_role(user_id, new_role)

            # --- 5. 성공 응답 데이터 생성 ---
            user_role_data = UserRoleUpdate.model_validate(update_user, from_attributes=True)

            await self.user_repo.db.commit()

            return UserRoleChangeResponse(
                success=True,
                data=user_role_data
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_user_role service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin update_user_role service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )


    async def update_user_status(self, user_id:str, new_status:UserStatus) -> Union[UserStatusChangeResponse, ErrorResponse]:
        try:
            pass
            # --- 1. 사용자 조회 ---
            user = await self.user_repo.get_user_by_id(user_id)

            # --- 2. 사용자가 없는 경우 Not Found 에러 반환 ---
            if not user:
                return ErrorResponse(
                    error = ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
                    )
                )
            
            # --- 3. ADMIN 게정의 상태 변경 방지 로직 ---
            if user.role == UserRole.ADMIN:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.FORBIDDEN,
                        message=Message.FORBIDDEN
                    )
                )

            # --- 4. 리포지토리를 통해 상태 업데이트 ---
            update_user = await self.user_repo.update_user_status(user_id, new_status)

            # --- 5. 성공 응답 데이터 생성 ---
            user_status_data = UserStatusUpdate.model_validate(update_user, from_attributes=True)

            await self.user_repo.db.commit()

            return UserStatusChangeResponse(
                success=True,
                data=user_status_data
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_user_status service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin update_user_status service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )