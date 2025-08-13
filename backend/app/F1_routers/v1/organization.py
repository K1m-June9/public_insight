import logging

from fastapi import APIRouter, Depends, HTTPException
from typing import Union
from fastapi.responses import JSONResponse
from app.F2_services.organization import OrganizationService
from app.F5_core.dependencies import get_organization_service
from app.F6_schemas.organization import OrganizationListResponse, OrganizationCategoryResponse, OrganizationIconResponse, WordCloudResponse, EmptyWordCloudResponse, OrganizationSummaryResponse
from app.F6_schemas.base import ErrorResponse, ErrorCode

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=OrganizationListResponse)
async def get_organizations(org_service: OrganizationService = Depends(get_organization_service)):
    """
    메인페이지 기관 목록 조회
    
    원형 그래프를 구성하는 기관 목록과 비율을 조회합니다.
    활성화된 기관들의 피드 개수를 기반으로 비율을 계산하여 95%로 스케일링하고,
    나머지 5%는 "기타" 항목으로 할당하여 총 100% 구성합니다.
    
    Returns:
        OrganizationListResponse: 기관 목록과 각 기관별 비율 정보
        
    Raises:
        HTTPException: 서버 내부 오류 발생 시 500 상태 코드 반환
    """
    result = await org_service.get_organizations_for_chart()
    if isinstance(result, ErrorResponse):
        return JSONResponse(status_code=500, content=result.model_dump())
    
    return result

@router.get("/{name}/summary", response_model=OrganizationSummaryResponse)
async def get_organization_summary(name: str, org_service: OrganizationService = Depends(get_organization_service)):
    """
    기관 상세 페이지 헤더 요약 정보 조회
    
    기관의 기본 정보(이름, 설명)와 통합 통계(총 문서 수, 총 조회수, 평균 만족도)를 제공
    """
    result = await org_service.get_organization_summary(name)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    return result
    
@router.get("/{name}/categories", response_model=OrganizationCategoryResponse)
async def get_organization_categories(name: str, org_service: OrganizationService = Depends(get_organization_service)):
    """
    기관별 카테고리 목록 조회
    
    특정 기관의 카테고리 목록과 비율을 조회합니다.
    해당 기관의 활성화된 카테고리들의 피드 개수를 기반으로 비율을 계산하여 95%로 스케일링하고,
    나머지 5%는 "기타" 항목으로 할당하여 총 100% 구성합니다.
    
    Args:
        name (str): 조회할 기관의 이름 (예: "국회")
        organization_service: 기관 서비스 의존성 주입
        
    Returns:
        OrganizationCategoryResponse: 기관 정보와 카테고리별 비율 정보
        
    Raises:
        HTTPException: 서버 내부 오류 발생 시 500 상태 코드 반환
        
    Example:
        GET /api/organizations/국회/categories
    """
    result = await org_service.get_organization_categories_for_chart(name)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/{name}/icon", response_model=OrganizationIconResponse)
async def get_organization_icon(name: str, org_service: OrganizationService = Depends(get_organization_service)):
    """
    기관 아이콘 조회
    
    기관 원형 그래프 중앙에 표시할 아이콘을 Base64 형식으로 조회합니다.
    파일 시스템에서 .ico 파일을 읽어 Data URL 형식으로 변환하여 반환합니다.
    
    Args:
        name (str): 조회할 기관의 이름 (예: "국회")
        organization_service: 기관 서비스 의존성 주입
        
    Returns:
        OrganizationIconResponse: 기관 정보와 Base64 인코딩된 아이콘 데이터
        
    Raises:
        HTTPException: 
            - 404: 존재하지 않는 기관
            - 500: 아이콘 파일 로드 오류 또는 서버 내부 오류
        
    Example:
        GET /api/organizations/국회/icon
    """
    result = await org_service.get_organization_icon(name)
    if isinstance(result, ErrorResponse):
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result

@router.get("/{name}/wordcloud", response_model=WordCloudResponse)
async def get_organization_wordcloud(name: str, org_service: OrganizationService = Depends(get_organization_service)):
    """
    기관별 주요 키워드(워드클라우드용) 조회
    
    score가 높은 순으로 상위 14개 키워드를 조회하여,
    UI 렌더링에 필요한 text, size, color, weight 정보를 함께 반환
    """
    result = await org_service.get_organization_wordcloud(name)
    
    if isinstance(result, ErrorResponse):
        # 💡 NOT_FOUND 에러도 처리할 수 있도록 분기 추가
        status_code = 404 if result.error.code == ErrorCode.NOT_FOUND else 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    return result