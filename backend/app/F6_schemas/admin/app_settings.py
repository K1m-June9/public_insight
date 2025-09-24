from pydantic import BaseModel, ConfigDict
from datetime import datetime 
from typing import Optional 

from app.F6_schemas.base import BaseSchema, BaseResponse


# ========================================
# 1. 앱 설정 기본 스키마
# ========================================
class AppSettingBase(BaseSchema):
    """
    앱 설정 기본 스키마
    - 공통 필드 정의
    """
    key_name: str               # 설정 키 이름
    key_value: str              # 설정 값
    description: Optional[str] = None   # 설정 설명(선택)
    is_active: bool = True      # 활성화 여부


# ========================================
# 2. 앱 설정 생성 및 수정 스키마
# ========================================

class AppSettingCreateRequest(AppSettingBase):
    """
    앱 설정 생성 요청 스키마
    - AppSettingBase 필드 그대로 사용
    """
    pass

class AppSettingUpdateRequest(AppSettingBase):
    """
    앱 설정 수정 요청 스키마
    - key_name은 수정 불가, 나머지만 허용
    """
    key_name: str
    key_value: str 
    description: Optional[str] = None 
    is_active: bool = True 


# ========================================
# 3. 앱 설정 조회 및 응답 스키마
# ========================================

class AppSettingResponse(AppSettingBase):
    """
    앱 설정 단건 조회 및 응답 스키마
    """
    id: int                 # 설정 ID
    created_at: datetime    # 생성 일시
    updated_at: datetime    # 수정 일시

    model_config = ConfigDict(from_attributes=True)

class AppSettingDeleteResponse(BaseResponse):
    """슬라이더 삭제 응답"""
    success: bool = True
    message: str = "성공적으로 삭제되었습니다."



