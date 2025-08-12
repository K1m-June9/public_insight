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

from app.F3_repositories.admin.slider import SliderAdminRepository
from app.F3_repositories.admin.activity_log import UsersActivityRepository 
from app.F5_core.config import settings
from app.F6_schemas.admin.slider import (
    SliderListResponse,
    SliderListItem,
    SliderDetailResponse,
    SliderDetail,
    SliderCreateRequest,
    SliderCreateResponse,
    SliderUpdateRequest,
    SliderUpdateResponse,
    SliderStatusUpdateRequest,
    SliderStatus,
    SliderStatusUpdateResponse,
    SliderStatusUpdateResponseData,
    SliderDeleteResponse,

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
from app.F7_models.users import User

logger = logging.getLogger(__name__)

class SliderAdminService:
    def __init__(self, repo: SliderAdminRepository):
        self.repo = repo
        self.slider_basic_image="947f932a-32ca-4593-acae-23fcef7584e6.jpg"
    
    def _create_image_url(self, image_path: str | None) -> str | None:
        """DB에 저장된 이미지 파일 이름을 완전한 웹 URL로 변환(파일이 없으면 None)"""
        if not image_path:
            return f"{Settings.STATIC_FILES_URL}/sliders/{self.slider_basic_image}"
        
        return f"{Settings.STATIC_FILES_URL}/sliders/{image_path}"
    
                
    async def _save_image_to_disk(self, image_file: UploadFile) -> str:
        """이미지 파일을 디스크에 저장하고 고유한 파일 이름을 반환"""
        try:
            file_extension = Path(image_file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # settings.SLIDER_STORAGE_PATH가 .env에 정의되어 있어야 함
            # 경로 수정해야함
            save_dir = Path(Settings.SLIDER_STORAGE_PATH)
            save_dir.mkdir(parents=True, exist_ok=True)
            file_path = save_dir / unique_filename

            # UploadFile의 content를 직접 파일에 씁니다.
            async with open(file_path, "wb") as f:
                await f.write(image_file.file.read())
            
            logger.info(f"Successfully saved image to {file_path}")
            return unique_filename 
        
        except Exception as e:
            logger.error(f"Failed to save slider image to disk: {e}", exc_info=True)
            raise # 에러를 다시 발생시켜 상위 try-except에서 처리하도록 함


    async def _delete_image_from_disk(self, filename: str):
        """주어진 파일명에 해당하는 이미지 파일을 디스크에서 삭제"""
        if not filename or filename == self.slider_basic_image:
            # 파일명이 없거나 기본 이미지인 경우 삭제하지 않음
            logger.info(f"Skipping deletion for default or empty filename: {filename}")
            return 
        
        try:
            # --- 1. 삭제할 파일의 전체 경로 생성 ---
            slider_dir = Path(Settings.SLIDER_STORAGE_PATH)
            file_path = slider_dir / filename

            # --- 2. 파일의 존재 유무 확인 ----
            if file_path.is_file():
                # --- 3. 파일 삭제 ----
                os.remove(file_path)
                logger.info(f"Successfully deleted image file: {file_path}")
            else:
                # 파일이 존재하지 않는 경우, 경고 로그만 남김
                logger.warning(f"Image file not found for deletion, but proceeding: {file_path}")

        except Exception as e:
            logger.error(f"Error deleting image file {filename}: {e}", exc_info=True)

    async def get_slider_list(self) -> Union[SliderListResponse, ErrorResponse]:
        """전체 슬라이더 목록을 조회"""
        try:
            # --- 1. 리포지토리를 통해 모든 슬라이더 데이터 조회 ---
            sliders_from_db = await self.repo.get_all_sliders()

            # --- 2. 조회된 ORM 객체 리스트를 SlierListItem 리스트로 변환 ---
            slider_list_items = []
            for slider in sliders_from_db:
                slider_item = SliderListItem.model_validate(slider, from_attributes=True)
                slider_item.image_path = self._create_image_url(slider.image_path)
                slider_list_items.append(slider_item)

            # --- 3. 최종 성공 응답 객체 생성 ---
            return SliderListResponse(
                success=True,
                data=slider_list_items
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_user_list service:{e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_user_list service: {e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        

    async def get_slider_detail(self, slider_id:int) -> Union[SliderDetailResponse, ErrorResponse]:
        """슬라이더 상세 조회"""
        try:
            # --- 1. 리포지토리를 통해 ID로 슬라이더 데이터 조회 ---
            slider = await self.repo.get_slider_by_id(slider_id)

            # --- 2. 슬라이더가 없는 경우 Not Found 데이터 조회 ---
            if not slider:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )

            # --- 3. 이미지 파일을 읽어 Base64로 인코딩 ---
            image_url = self._create_image_url(slider.image_path)

            # --- 4. 최종 SliderDetail 응답 데이터 생성 ---
            slider_detail_data = SliderDetail(
                id=slider.id,
                title=slider.title,
                preview=slider.preview,
                tag=slider.tag,
                content=slider.content,
                author=slider.author,
                image=image_url,
                display_order=slider.display_order,
                is_active=slider.is_active,
                start_date=slider.start_date,
                end_date=slider.end_date,
                created_at=slider.created_at,
                updated_at=slider.updated_at,
            )

            return SliderDetailResponse(
                success=True,
                data=slider_detail_data
            )
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin get_user_list service:{e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin get_user_list service: {e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        

    async def create_slider(
        self, 
        request_data:SliderCreateRequest, 
        image_file: Optional[UploadFile]
    ) -> Union[SliderCreateResponse, ErrorResponse]:
        """관리자: 새로운 슬라이더를 생성"""
        try:
            image_filename_to_db = self.slider_basic_image

            # --- 1. 이미지 파일 처리 및 유효성 검사 ---
            if image_file and image_file.filename:
                # 파일 크기 초과
                if image_file.size > Settings.MAX_FILE_SIZE:
                    return ErrorResponse(
                        error = ErrorDetail(
                            code=ErrorCode.FILE_TOO_LARGE,
                            message=Message.FILE_TOO_LARGE
                        )
                    )
                
                # --- 2. 이미지 파일 처리(배포/개발 환경 공통) ---
                try:
                    # 배포 환경
                    if settings.ENVIRONMENT == "production":
                        image_filename_to_db = await self._save_image_to_disk(image_file)
                    # 개발 환경
                    else:
                        logger.info(f"Dev env: Skipping save for '{image_file.filename}'.")
                except Exception as e:
                    logger.error(f"Failed to save image file '{image_file.filename}': {e}", exc_info=True)

                    return ErrorResponse(
                        error=ErrorDetail(
                            code=ErrorCode.INTERNAL_ERROR,
                            message="이미지 파일 처리 중 서버 오류가 발생했습니다."
                        )
                    )
                
            # --- 3. DB에 최종 데이터 생성 ---
            slider_data_dict = request_data.model_dump()
            slider_data_dict['image_path'] = image_filename_to_db
            slider_data_dict['author'] = "관리자" # 주의
            slider_data_dict['is_active'] = True

            new_slider = await self.repo.create_slider(slider_data_dict)

            # --- 4. 성공 응답 데이터 생성 ---
            slider_response_data = SliderDetail(
                id=new_slider.id,
                title=new_slider.title,
                preview=new_slider.preview,
                tag=new_slider.tag,
                content=new_slider.content,
                author=new_slider.author,
                image=self._create_image_url(new_slider.image_path),
                display_order=new_slider.display_order,
                is_active=new_slider.is_active,
                start_date=new_slider.start_date,
                end_date=new_slider.end_date,
                created_at=new_slider.created_at,
                updated_at=new_slider.updated_at
                )

            return SliderCreateResponse(
                success=True,
                data=slider_response_data
            )
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin create_slider service:{e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin create_slider service: {e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )


    async def update_slider(
            self, 
            slider_id: int, 
            request_data: SliderUpdateRequest,
            image_file: Optional[UploadFile]
    )-> Union[SliderUpdateResponse, ErrorResponse]:
        """특정 슬라이더의 정보를 업데이트"""
        try:
            # --- 1. DB에서 수정할 슬라이더 찾기 ---
            slider_to_update = await self.repo.get_slider_by_id(slider_id)

            # --- 2. 슬라이더가 없는 경우 Not Found 데이터 조회 ---
            if not slider_to_update:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 3. 새 이미지 파일 처리 및 유효성 검사 ---
            new_image_path = slider_to_update.image_path # 기본값은 기존 이미지 경로

            if image_file and image_file.filename:
                
                if image_file.size > Settings.MAX_FILE_SIZE:
                    return ErrorResponse(
                        error=ErrorDetail(
                            code=ErrorCode.FILE_TOO_LARGE,
                            message=Message.FILE_TOO_LARGE
                        )
                    )
                
                # 파일 저장 로직
                try:
                    # 배포 환경
                    if settings.ENVIRONMENT == "production":
                        if slider_to_update.image_path != self.slider_basic_image:
                            await self._delete_image_from_disk(slider_to_update.image_path)
                        new_image_path = await self._save_image_to_disk(image_file)
                    # 개발 환경
                    else: 
                        logger.info(f"Dev env: Skipping update for image '{image_file.filename}'.")
                        new_image_path = f"dev_updated_{image_file.filename}"
                except Exception as e:
                    logger.error(f"Failed to process image file for slider {slider_id}: {e}", exc_info=True)
                    return ErrorResponse(
                        error=ErrorDetail(
                            code=ErrorCode.INTERNAL_ERROR,
                            message=Message.INTERNAL_ERROR
                        )
                    )

            # --- 4. 업데이트할 데이터 준비 ---
            update_data_dict = request_data.model_dump(exclude_unset=True, exclude_none=True)

            # 새 이미지 경로가 결정되었다면 업데이트 데이터에 추가
            if new_image_path != slider_to_update.image_path:
                update_data_dict['image_path'] = new_image_path 
            

            # 만약 테스트와 이미지 모두 수정할 데이터가 없다면
            # 현재 데이터를 그대로 반환하여 불필요한 DB 업데이트 방지
            if not update_data_dict:
                logger.info(f"No fields to update for slider ID: {slider_id}. Returning current data.")


                # 현재 데이터를 응답 형식에 맞게 가공하여 반환
                response_data_without_update = SliderDetail.model_validate(slider_to_update, from_attributes=True)

                response_data_without_update.image = self._create_image_url(slider_to_update.image_path)

                return SliderUpdateResponse(
                    success=True, 
                    data=response_data_without_update
                )
            
            # --- 5. 리포지토리를 통해 DB 업데이트 ---
            updated_slider = await self.repo.update_slider(
                slider=slider_to_update,
                update_data=update_data_dict
            )
            
            # --- 6. 최종 응답 데이터 조립 ---
            response_data_dict = SliderDetail(
                id=updated_slider.id,
                title=updated_slider.title,
                preview=updated_slider.preview,
                tag=updated_slider.tag,
                content=updated_slider.content,
                author=updated_slider.author,
                image=self._create_image_url(updated_slider.image_path),
                display_order=updated_slider.display_order,
                is_active=updated_slider.is_active,
                start_date=updated_slider.start_date,
                end_date=updated_slider.end_date,
                created_at=updated_slider.created_at,
                updated_at=updated_slider.updated_at
                )

            response_data = SliderDetail.model_dump(response_data_dict)
            return SliderUpdateResponse(
                success=True,
                data=response_data
            )

        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_slider service:{e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            # await self.repo.db.rollback()
            logger.error(f"Error in Admin update_slider service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
    

    async def update_slider_status(self, slider_id: int, is_active: bool) -> Union[SliderStatusUpdateResponse, ErrorResponse]:
        """특정 슬라이더의 is_active 상태만 업데이트"""
        try:
            # --- 1. DB에서 수정할 슬라이더 찾기 ---
            slider_to_update = await self.repo.get_slider_by_id(slider_id)
            
            # --- 2. 슬라이더가 없는 경우 Not Found 데이터 조회 ---
            if not slider_to_update:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )

            # --- 3. 리포지토리를 통해 상태 업데이트 ---
            updated_slider = await self.repo.update_slider_status(
                slider=slider_to_update,
                is_active=is_active
            )

            # --- 4. 성공 응답 데이터 생성 ---
            response_data = SliderStatusUpdateResponseData.model_validate(updated_slider, from_attributes=True)


            return SliderStatusUpdateResponse(
                success=True,
                data=response_data
            )
        
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin update_slider_status service:{e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin update_slider_status service: {e}", exc_info=True)
            # await self.repo.db.rollback()
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
        
    
    async def delete_slider(self, slider_id:int) -> Union[SliderDeleteResponse, ErrorResponse]:
        """특정 슬라이더와 연관된 이미지 파일 삭제"""
        try:
            # --- 1. DB에서 삭제할 슬라이더 찾기 ---
            slider_to_delete = await self.repo.get_slider_by_id(slider_id)

            # --- 2. 슬라이더가 없는 경우 Not Found 데이터 조회 ---
            if not slider_to_delete:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.NOT_FOUND
                    )
                )
            # --- 3. 연관된 이미지 파일 삭제(DB 삭제 전에 수행) ---
            try:
                image_path_to_delete = slider_to_delete.image_path 
                await self._delete_image_from_disk(image_path_to_delete)
            except Exception as e:
                logger.warning(
                    f"Could not delete image file {image_path_to_delete} for slider ID {slider_id}. "
                    f"Proceeding with DB record deletion. Error: {e}", exc_info=True
                )
        
            # --- 4. 리포지토리를 통해 DB 레코드 삭제 ---
            delete_success = await self.repo.delete_slider(slider=slider_to_delete)

            if not delete_success:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INTERNAL_ERROR, 
                        message=Message.INTERNAL_ERROR
                    )
                )
            
            else:
                return SliderDeleteResponse(
                    success=True,
                    message=Message.DELETED
                )


            # --- 5. 성공 응답 반환 ---
        except SQLAlchemyError as e:
            logger.error(f"Database error in Admin delete_slider service:{e}", exc_info=True)
            return ErrorResponse(
                error = ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )

        except Exception as e:
            logger.error(f"Error in Admin delete_slider service: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )