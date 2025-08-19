from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from typing import Union
import logging

from app.F2_services.slider import SliderService
from app.F5_core.dependencies import get_slider_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F6_schemas.slider import SliderListResponse, SliderDetailResponse
from app.F6_schemas.base import ErrorResponse, ErrorCode

logger = logging.getLogger(__name__)

router = APIRouter()

# 메인페이지 슬라이더 목록 조회 엔드포인트
@router.get("", response_model=SliderListResponse)
@log_event_detailed(action="LIST", category=["PUBLIC", "SLIDER"])
async def get_sliders(
    slider_service: SliderService = Depends(get_slider_service)
):
    """
    메인페이지 우측 상단 슬라이더 목록 조회
    
    - **목적**: 메인페이지에 표시할 활성화된 슬라이더 목록 반환
    - **인증**: 불필요
    - **권한**: 없음 (모든 사용자 접근 가능)
    - **응답**: 슬라이더 목록과 base64 인코딩된 이미지 데이터
    """
    result = await slider_service.get_active_sliders_list()
    
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
        
    return result

# 슬라이더 상세 조회 엔드포인트
@router.get("/{id}", response_model=Union[SliderDetailResponse, ErrorResponse])
@log_event_detailed(action="READ", category=["PUBLIC", "SLIDER", "DETAIL"])
async def get_slider_detail(
    id: int,
    slider_service: SliderService = Depends(get_slider_service)
):
    """
    슬라이더 상세 페이지의 모든 내용 조회
    
    - **목적**: 슬라이더 상세 정보 반환 (제목, 내용, 이미지, 작성자 등)
    - **인증**: 불필요
    - **권한**: 없음 (모든 사용자 접근 가능)
    - **응답**: 슬라이더 상세 정보와 base64 인코딩된 이미지 데이터
    """
    result = await slider_service.get_slider_detail(id)
    
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
        
    return result