import logging 
from sqlalchemy.ext.asyncio import AsyncSession 

from app.F3_repositories.admin.app_settings import AppSettingRepository
from app.F6_schemas.base import ErrorResponse, ErrorCode, ErrorDetail, Message
from app.F6_schemas.admin.app_settings import AppSettingCreateRequest, AppSettingUpdateRequest, AppSettingResponse, AppSettingDeleteResponse 
from app.F7_models.app_settings import AppSettings 


logger = logging.getLogger(__name__)

class AppSettingService:
    def __init__(self, setting_repository: AppSettingRepository):
        self.setting_repo = setting_repository

    async def get_nlp_server_url(self) -> str | None:
        setting = await self.setting_repo.get_by_key_name("NLP_SERVER_URL")

        if setting and setting.is_active:
            return setting.key_value
        
        return None

    async def create_setting(self, setting_in: AppSettingCreateRequest)-> AppSettingResponse:
        """
        새로운 앱 설정 생성
        """
        try: 
            # --- 1. 중복 키 검사 ---
            if await self._is_duplicate_key(setting_in.key_name):
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.DUPLICATE,
                        message=Message.DUPLICATE_KEY_NAME
                    )
                )
            
            # --- 2. DB에 생성 ---
            new_setting = await self.setting_repo.create(setting_in)

            # --- 3. Response 객체로 변환 ---
            return AppSettingResponse.model_validate(new_setting)
        
        except Exception as e:
            logger.error(f"Error in Internal create_setting: {e}", exc_info=True)

            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )
    

    async def get_app_setting(self, key_name: str) -> AppSettingResponse:
        """
        단일 설정 조회
        """
        try:
            # --- 1. DB에서 설정 조회 ---
            setting = await self.setting_repo.get_by_key_name(key_name)
            if not setting:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 2. Response 객체로 변환 ---
            return AppSettingResponse.model_validate(setting)

        except Exception as e:
            logger.error(f"Error in Internal get_app_setting: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )



    async def update_setting(self, key_name: str, setting_in: AppSettingUpdateRequest) -> AppSettingResponse:
        """
        단일 설정 업데이트
        """
        try:
            # --- 1. DB에서 설정 조회 ---
            setting = await self.setting_repo.get_by_key_name(key_name)
            if not setting:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            # --- 2. DB 업데이트 ---
            update_setting = await self.setting_repo.update(key_name, setting_in)

            # --- 3. Response 객체로 변환 ---
            return AppSettingResponse.model_validate(update_setting)

        except Exception as e:
            logger.error(f"Error in Internal update_setting: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )


    
    async def delete_setting(self, key_name: str) -> AppSettingDeleteResponse:
        """
        단일 설정 삭제
        """
        try: 
            # --- 1. DB에서 설정 조회 ---
            setting = await self.setting_repo.get_by_key_name(key_name)
            if not setting:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            delete_setting = await self.setting_repo.delete(key_name)

            return AppSettingDeleteResponse()

        except Exception as e:
            logger.error(f"Error in Internal delete_setting: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                    )
                )

    
    # ============================
    # 내부 함수
    # ============================
    async def _is_duplicate_key(self, key_name: str) -> bool:
        """
        주어진 key_name이 이미 존재하는지 여부를 확인
        """
        existing_setting = await self.setting_repo.get_by_key_name(key_name)
        return existing_setting is not None