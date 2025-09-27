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

from app.F3_repositories.admin.notices import NoticesAdminRepository
from app.F3_repositories.admin.activity_log import UsersActivityRepository 
from app.F5_core.config import settings
from app.F7_models.users import User
from app.F6_schemas.admin.notices import (
    NoticeStatus,
    NoticeListItem,
    NoticeDetail,
    NoticeCreateRequest,
    NoticeUpdateRequest,
    NoticePinUpdateRequest,
    NoticeStatusUpdateRequest,
    NoticeListResponse,
    NoticeDetailResponse,
    NoticeCreateResponse,
    NoticeUpdateResponse,
    NoticeDeleteResponse,
    NoticePathParams,
    NoticePinStateUpdateRequest
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
    UserRole,
)


logger = logging.getLogger(__name__)

class NoticesAdminService:
    def __init__(self, repo: NoticesAdminRepository):
        self.repo = repo 
    
    async def get_notice_list(self, current_user:User) -> Union[NoticeListResponse,ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            # --- 2. 전체 notice 조회(고정 공지사항, 최신순으로 정렬) ---
            notices_from_db = await self.repo.get_all_notices()

            # --- 3. 조회된 ORM 객체 리스트를 NoticeListItem 리스트로 변환---
            notice_list_items = []
            for notice in notices_from_db:
                notice_item = NoticeListItem.model_validate(notice, from_attributes=True)
                notice_list_items.append(notice_item)
                
            # --- 4. 최종 성공 응답 객체 생성---
            return NoticeListResponse(
                success=True,
                data=notice_list_items
            )
        
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_notice_list service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_notice_list service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def get_notice_detail(self, current_user:User, notice_id:int) -> Union[NoticeDetailResponse, ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            
            # --- 2. 리포지토리를 통해 ID로 notice 데이터 조회 ---
            notice = await self.repo.get_notice_by_id(notice_id)

            # --- 3. notice가 없는 경우 Not Found 데이터 조회 ---
            if not notice:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 4. 최종 NoticeDetail 응답 데이터 생성 ---
            notice_response_data = NoticeDetail.model_validate(notice, from_attributes=True)

            return NoticeDetailResponse(
                success=True,
                data=notice_response_data
            )
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_notice_detail service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_notice_detail service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def create_notice(self, current_user:User, request_data:NoticeCreateRequest) -> Union[NoticeCreateResponse, ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            
            # --- 2. 생성할 최종 데이터 생성 ---
            notice_data_dict = request_data.model_dump()
            notice_data_dict['author'] = current_user.user_id

            new_notice = await self.repo.create_notice(notice_data_dict)

            await self.repo.db.commit()
            await self.repo.db.refresh(new_notice)

            
            # --- 3. 성공 응답 데이터 생성 ---
            notice_response_data = NoticeDetail(
                id=new_notice.id,
                title=new_notice.title,
                content=new_notice.content,
                author=new_notice.author,
                is_pinned=new_notice.is_pinned,
                is_active=new_notice.is_active,
                view_count=new_notice.view_count,
                created_at=new_notice.created_at,
                updated_at=new_notice.updated_at
            )


            return NoticeCreateResponse(
                success=True,
                data=notice_response_data
            )
        
        except SQLAlchemyError as e:
            await self.repo.db.rollback()
            logger.error(f"Database error in Admin create_notice service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in Admin create_notice service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def update_notice(self, current_user:User, notice_id:int, request_data:NoticeUpdateRequest) -> Union[NoticeUpdateResponse, ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            
            # --- 2. 리포지토리를 통해 ID로 notice 데이터 조회 ---
            notice = await self.repo.get_notice_by_id(notice_id)

            # --- 3. notice가 없는 경우 Not Found 데이터 조회 ---
            if not notice:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 4. 수정할 공지사항 최종 데이터 생성 ---
            update_data_dict = request_data.model_dump()
            # update_data_dict['author'] = current_user.user_id

            update_notice = await self.repo.update_notice(
                notice=notice,
                update_data=update_data_dict
            )

            # --- 5. 성공 응답 데이터 생성 ---
            notice_response_data = NoticeDetail(
                id=update_notice.id,
                title=update_notice.title,
                content=update_notice.content,
                author=update_notice.author,
                is_pinned=update_notice.is_pinned,
                is_active=update_notice.is_active,
                view_count=update_notice.view_count,
                created_at=update_notice.created_at,
                updated_at=update_notice.updated_at
            )

            await self.repo.db.commit()
            await self.repo.db.refresh(update_notice)

            return NoticeUpdateResponse(
                success=True,
                data=notice_response_data
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_notice service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin update_notice service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    async def update_notice_status(self, current_user:User, notice_id, request_data:NoticePinStateUpdateRequest) -> Union[NoticeUpdateResponse, ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            
            # --- 2. 리포지토리를 통해 ID로 notice 데이터 조회 ---
            notice_to_update = await self.repo.get_notice_by_id(notice_id)

            # --- 3. notice가 없는 경우 Not Found 데이터 조회 ---
            if not notice_to_update:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 4. 수정할 공지사항 최종 데이터 생성 ---
            update_data_dict = request_data.model_dump(exclude_unset=True)

            if update_data_dict:
                final_notice_obj = await self.repo.update_notice(
                    notice=notice_to_update,
                    update_data=update_data_dict
                )


            # --- 5. 성공 응답 데이터 생성 ---
            # notice_response_data = NoticeDetail(
            #     id=update_notice.id,
            #     title=update_notice.title,
            #     content=update_notice.content,
            #     author=update_notice.author,
            #     is_pinned=update_notice.is_pinned,
            #     is_active=update_notice.is_active,
            #     view_count=update_notice.view_count,
            #     created_at=update_notice.created_at,
            #     updated_at=update_notice.updated_at
            # )
            notice_response_data = NoticeDetail.model_validate(final_notice_obj, from_attributes=True)

            return NoticeUpdateResponse(
                success=True,
                data=notice_response_data
            )


        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_notice_status service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin update_notice_status service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        

    async def delete_notice(self,current_user:User, notice_id:int) -> Union[NoticeDeleteResponse, ErrorResponse]:
        try:
            # # --- 1. 계정 ADMIN 인지 체크 ---
            # if current_user.role != UserRole.ADMIN:
            #     return ErrorResponse(
            #         error=ErrorDetail(
            #             code=ErrorCode.FORBIDDEN,
            #             message=Message.FORBIDDEN
            #         )
            #     )
            
            # --- 2. 리포지토리를 통해 ID로 notice 데이터 조회 ---
            notice_to_delete = await self.repo.get_notice_by_id(notice_id)

            # --- 3. notice가 없는 경우 Not Found 데이터 조회 ---
            if not notice_to_delete:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            # --- 4. 고정된 공지사항 식별 ---
            if notice_to_delete.is_pinned:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.FORBIDDEN,
                        message=Message.PINNED_NOTICE_DELETE_FORBIDDEN
                    )
                )
            
            # --- 5. 리포지토리를 통해 DB 레코드 삭제 ---
            delete_success = await self.repo.delete_notice(notice=notice_to_delete)

            if not delete_success:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INTERNAL_ERROR, 
                        message=Message.INTERNAL_ERROR
                    )
                )
            else:
                await self.repo.db.commit()
                return NoticeDeleteResponse(
                    success=True,
                    message=Message.DELETED
                )

        except SQLAlchemyError as e:
            await self.repo.db.rollback()
            logger.error(f"Database error in Admin delete_notice service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            await self.repo.db.rollback()
            logger.error(f"Error in Admin delete_notice service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )