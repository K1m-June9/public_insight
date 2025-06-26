import os
import base64
import mimetypes
from datetime import datetime
from typing import List, Optional
import logging
from pathlib import Path

from app.F3_repositories.slider import SliderRepository
from app.F6_schemas.slider import SliderListResponse, SliderListData, SliderListItem, SliderDetail, SliderDetailData, SliderDetailResponse
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

class SliderService:
    def __init__(self, slider_repository: SliderRepository):
        self.slider_repository = slider_repository
        self.image_base_path = Path("backend/app/sliders")
        self.default_image_name = "default"
    
    # 활성화된 슬라이더 목록 조회 서비스 메서드
    # 입력: 없음
    # 반환: SliderListResponse - 슬라이더 목록과 base64 인코딩된 이미지를 포함한 응답
    # 설명: 
    #   현재 시간을 기준으로 활성화된 슬라이더들을 조회하고,
    #   각 슬라이더의 이미지를 base64로 인코딩하여 응답 스키마에 맞게 변환
    #   이미지 처리 실패 시 해당 슬라이더는 목록에서 제외
    async def get_active_sliders_list(self) -> SliderListResponse:
        try:
            # 현재 시간을 기준으로 활성화된 슬라이더 조회
            current_time = datetime.utcnow()
            sliders = await self.slider_repository.get_active_sliders(current_time)
            
            # 슬라이더 목록을 스키마에 맞게 변환
            slider_items = []
            for slider in sliders:
                try:
                    # 이미지를 base64로 변환
                    image_base64 = await self._convert_image_to_base64(slider.image_path)
                    
                    # SliderListItem 스키마로 변환
                    slider_item = SliderListItem(
                        id=slider.id,
                        title=slider.title,
                        preview=slider.preview or "",  # preview가 None인 경우 빈 문자열
                        image=image_base64,
                        display_order=slider.display_order
                    )
                    slider_items.append(slider_item)
                    
                except Exception as e:
                    # 개별 슬라이더 처리 실패 시 로그 남기고 해당 슬라이더만 제외
                    logger.warning(f"Failed to process slider {slider.id}: {e}")
                    continue
            
            # 응답 데이터 구성
            slider_data = SliderListData(sliders=slider_items)
            return SliderListResponse(success=True, data=slider_data)
            
        except Exception as e:
            logger.error(f"Failed to get active sliders list: {e}", exc_info=True)
            raise
    
    # 슬라이더 상세 정보 조회 서비스 메서드
    # 입력: slider_id - 조회할 슬라이더의 고유 식별자 (int)
    # 반환: SliderDetailResponse - 슬라이더 상세 정보와 base64 인코딩된 이미지를 포함한 응답
    # 설명: 
    #   주어진 ID의 슬라이더 상세 정보를 조회하고,
    #   이미지를 base64로 인코딩하여 응답 스키마에 맞게 변환
    #   ID 검증, 존재 여부 확인, 활성화 상태 등을 종합적으로 처리
    async def get_slider_detail(self, slider_id: int) -> SliderDetailResponse:
        try:
            # 1. ID 유효성 검증
            if slider_id <= 0:
                error_response = ErrorResponse(
                    error=ErrorDetail(
                        code="INVALID_SLIDER_ID",
                        message="올바르지 않은 슬라이더 ID입니다."
                    )
                )
                return error_response
            
            # 2. 현재 시간을 기준으로 슬라이더 조회
            current_time = datetime.utcnow()
            slider = await self.slider_repository.get_slider_by_id(slider_id, current_time)
            
            # 3. 슬라이더가 존재하지 않거나 비활성 상태인 경우
            if not slider:
                error_response = ErrorResponse(
                    error=ErrorDetail(
                        code="SLIDER_NOT_FOUND",
                        message="슬라이더를 찾을 수 없습니다."
                    )
                )
                return error_response
            
            # 4. 이미지를 base64로 변환
            image_base64 = await self._convert_image_to_base64(slider.image_path)
            
            # 5. SliderDetail 스키마로 변환
            slider_detail = SliderDetail(
                id=slider.id,
                title=slider.title,
                content=slider.content or "",  # content가 None인 경우 빈 문자열
                image=image_base64,
                author=slider.author,
                tag=slider.tag,
                created_at=slider.created_at
            )
            
            # 6. 응답 데이터 구성
            slider_data = SliderDetailData(slider=slider_detail)
            return SliderDetailResponse(success=True, data=slider_data)
            
        except Exception as e:
            logger.error(f"Failed to get slider detail for ID {slider_id}: {e}", exc_info=True)
            raise

    # 이미지 파일을 base64로 변환하는 내부 메서드
    # 입력: image_path - 이미지 파일 경로 (예: /sliders/{UUID})
    # 반환: str - Data URL 형식의 base64 인코딩된 이미지 데이터
    # 설명: 
    #   주어진 경로의 이미지 파일을 읽어 base64로 인코딩
    #   파일이 없거나 읽기 실패 시 기본 이미지 사용
    #   MIME 타입을 자동으로 추론하여 Data URL 형식으로 반환
    async def _convert_image_to_base64(self, image_path: Optional[str]) -> str:
        try:
            # 이미지 경로가 없는 경우 기본 이미지 사용
            if not image_path:
                return await self._get_default_image_base64()
            
            # 실제 파일 경로 구성 (image_path: /sliders/{UUID})
            file_path = self.image_base_path / image_path.lstrip('/')
            
            # 파일 존재 여부 확인
            if not file_path.exists() or not file_path.is_file():
                logger.warning(f"Image file not found: {file_path}")
                return await self._get_default_image_base64()
            
            # 파일 읽기 및 base64 인코딩
            with open(file_path, 'rb') as image_file:
                image_data = image_file.read()
            
            # MIME 타입 추론
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/jpeg'  # 기본값
            
            # base64 인코딩 및 Data URL 형식으로 반환
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
            
        except Exception as e:
            logger.warning(f"Failed to convert image to base64: {image_path}, error: {e}")
            return await self._get_default_image_base64()
    
    # 기본 이미지를 base64로 변환하는 내부 메서드
    # 입력: 없음
    # 반환: str - Data URL 형식의 기본 이미지 base64 데이터
    # 설명: 
    #   기본 이미지 파일(default)을 찾아 base64로 인코딩
    #   여러 확장자를 시도하여 존재하는 파일 사용
    #   모든 시도가 실패하면 빈 Data URL 반환
    async def _get_default_image_base64(self) -> str:
        # 일반적인 이미지 확장자들을 시도
        extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        for ext in extensions:
            default_path = self.image_base_path / f"{self.default_image_name}{ext}"
            if default_path.exists() and default_path.is_file():
                try:
                    with open(default_path, 'rb') as image_file:
                        image_data = image_file.read()
                    
                    # MIME 타입 추론
                    mime_type, _ = mimetypes.guess_type(str(default_path))
                    if not mime_type:
                        mime_type = 'image/jpeg'
                    
                    # base64 인코딩 및 Data URL 형식으로 반환
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    return f"data:{mime_type};base64,{base64_data}"
                    
                except Exception as e:
                    logger.warning(f"Failed to read default image {default_path}: {e}")
                    continue
        
        # 기본 이미지도 없는 경우 빈 Data URL 반환
        logger.error("No default image found")
        return "data:image/jpeg;base64,"