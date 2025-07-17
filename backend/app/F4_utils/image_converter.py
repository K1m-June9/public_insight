import base64
import mimetypes
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class ImageConverter:
    def __init__(self, base_path: str, default_image_name: str = "default"):
        self.image_base_path = Path(base_path)
        self.default_image_name = default_image_name

    # 이미지 파일을 base64로 변환하는 내부 메서드
    # 입력: image_path - 이미지 파일 경로 (예: /sliders/{UUID})
    # 반환: str - Data URL 형식의 base64 인코딩된 이미지 데이터
    # 설명: 
    #   주어진 경로의 이미지 파일을 읽어 base64로 인코딩
    #   파일이 없거나 읽기 실패 시 기본 이미지 사용
    #   MIME 타입을 자동으로 추론하여 Data URL 형식으로 반환
    async def to_base64(self, image_path: Optional[str]) -> str:
        # 이전에 SliderService에 있던 _convert_image_to_base64 로직 전체를 여기에 옮김
        # ... (로직 동일)
        # 마지막 에러 발생 시 return "" 또는 기본 이미지 base64를 반환하도록 수정할 수 있음
        try:
            if not image_path: return await self._get_default_base64()
            file_path = self.image_base_path / image_path.lstrip('/')
            if not file_path.is_file(): return await self._get_default_base64()
            
            with open(file_path, 'rb') as f:
                image_data = f.read()
            mime_type, _ = mimetypes.guess_type(str(file_path))
            mime_type = mime_type or 'image/jpeg'
            
            base64_data = base64.b64encode(image_data).decode('utf-8')
            return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            logger.warning(f"Image to base64 conversion failed: {image_path}, error: {e}")
            return await self._get_default_base64()

    # 기본 이미지를 base64로 변환하는 내부 메서드
    # 입력: 없음
    # 반환: str - Data URL 형식의 기본 이미지 base64 데이터
    # 설명: 
    #   기본 이미지 파일(default)을 찾아 base64로 인코딩
    #   여러 확장자를 시도하여 존재하는 파일 사용
    #   모든 시도가 실패하면 빈 Data URL 반환
    async def _get_default_base64(self) -> str:
        # 이전에 SliderService에 있던 _get_default_image_base64 로직 전체를 여기에 옮김
        # ... (로직 동일)
        extensions = ['.jpg', '.jpeg', '.png']
        for ext in extensions:
            default_path = self.image_base_path / f"{self.default_image_name}{ext}"
            if default_path.is_file():
                return await self.to_base64(f"{self.default_image_name}{ext}")
        return "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7" # 1x1 투명 픽셀