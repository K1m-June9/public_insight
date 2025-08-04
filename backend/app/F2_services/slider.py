from datetime import datetime
from typing import Union
import logging

from app.F3_repositories.slider import SliderRepository
from app.F6_schemas.slider import SliderListResponse, SliderListData, SliderListItem, SliderDetail, SliderDetailData, SliderDetailResponse
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

class SliderService:
    def __init__(self, slider_repository: SliderRepository):
        self.slider_repository = slider_repository
        # image_converter 더이상 사용 안함(이미지 전송 방식 변경)

    def _create_image_url(self, image_path: str | None) -> str:
        """파일 경로를 완전한 웹 URL로 변환하는 헬퍼 함수"""
        if not image_path:
            # 기본 이미지가 필요하다면, 그 경로를 settings에서 가져올 수 있음
            # return f"{Settings.STATIC_FILES_URL}/sliders/default.jpg"
            return f"{Settings.STATIC_FILES_URL}/sliders/default.jpg"
        return f"{Settings.STATIC_FILES_URL}/sliders/{image_path}"

    async def get_active_sliders_list(self) -> Union[SliderListResponse, ErrorResponse]:
        try:
            sliders = await self.slider_repository.get_active_sliders(datetime.utcnow())
            
            slider_items = []
            for slider in sliders:
                # 이미지 전달 방식 변경
                image_url = self._create_image_url(slider.image_path)
                
                slider_item = SliderListItem(
                    id=slider.id,
                    title=slider.title,
                    preview=slider.preview or "",
                    image=image_url,
                    display_order=slider.display_order
                )
                slider_items.append(slider_item)
            
            return SliderListResponse(
                success=True,
                data=SliderListData(sliders=slider_items)
            )
            
        except Exception as e:
            logger.error(f"Failed to get active sliders list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                    )
                )

    async def get_slider_detail(self, slider_id: int) -> Union[SliderDetailResponse, ErrorResponse]:
        try:
            if slider_id <= 0:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INVALID_PARAMETER,
                        message=Message.INVALID_PARAMETER
                    )
                )

            slider = await self.slider_repository.get_slider_by_id(slider_id, datetime.utcnow())
            
            if not slider:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND, 
                        message=Message.SLIDER_NOT_FOUND
                    )
                )

            image_url = self._create_image_url(slider.image_path)
            
            slider_detail = SliderDetail(
                id=slider.id,
                title=slider.title,
                content=slider.content or "",
                image=image_url,
                author=slider.author,
                tag=slider.tag,
                created_at=slider.created_at
            )
            
            return SliderDetailResponse(
                success= True, 
                data=SliderDetailData(slider=slider_detail)
            )
            
        except Exception as e:
            logger.error(f"Failed to get slider detail for ID {slider_id}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR, 
                    message=Message.INTERNAL_ERROR
                )
            )