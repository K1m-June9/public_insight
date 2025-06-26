from fastapi import APIRouter, Depends, Path
from fastapi.responses import JSONResponse
from typing import Union
import logging

from app.F2_services.slider import SliderService
from app.F5_core.dependencies import get_slider_service
from app.F6_schemas.slider import SliderListResponse, SliderDetailResponse
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message

logger = logging.getLogger(__name__)

router = APIRouter()

# 메인페이지 슬라이더 목록 조회 엔드포인트
@router.get("", response_model=SliderListResponse)
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
    try:
        # 1. 활성화된 슬라이더 목록 조회
        result = await slider_service.get_active_sliders_list()
        
        # 2. 성공 응답 반환
        return result
        
    except Exception as e:
        # 3. 예외 발생 시 로그 기록 및 에러 응답 반환
        logger.error(f"Failed to get sliders: {e}", exc_info=True)
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message=Message.INTERNAL_ERROR
            )
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

# 슬라이더 상세 조회 엔드포인트
@router.get("/{id}", response_model=Union[SliderDetailResponse, ErrorResponse])
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
    try:
        # 1. 슬라이더 상세 정보 조회
        result = await slider_service.get_slider_detail(id)
        
        # 2. 에러 응답인지 확인
        if isinstance(result, ErrorResponse):
            # 에러 코드에 따라 HTTP 상태코드 설정
            if result.error.code == "SLIDER_NOT_FOUND":
                status_code = 404
            elif result.error.code == "INVALID_SLIDER_ID":
                status_code = 400
            else:
                status_code = 500
            
            return JSONResponse(
                status_code=status_code,
                content=result.model_dump()
            )
        
        # 3. 성공 응답 반환
        return result
        
    except Exception as e:
        # 4. 예외 발생 시 로그 기록 및 에러 응답 반환
        logger.error(f"Failed to get slider detail for ID {id}: {e}", exc_info=True)
        
        error_response = ErrorResponse(
            error=ErrorDetail(
                code=ErrorCode.INTERNAL_ERROR,
                message=Message.INTERNAL_ERROR
            )
        )
        
        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )
