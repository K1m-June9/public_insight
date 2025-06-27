import logging

from fastapi import APIRouter, Depends, HTTPException
from typing import Union

from app.F2_services.organization import OrganizationService, OrganizationServiceException
from app.F5_core.dependencies import get_organization_service
from app.F6_schemas.organization import OrganizationListResponse, OrganizationCategoryResponse, OrganizationIconResponse, WordCloudResponse, EmptyWordCloudResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=OrganizationListResponse)
async def get_organizations(
    organization_service: OrganizationService = Depends(get_organization_service)
):
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
    try:
        # Service 레이어에서 기관 목록과 비율 데이터 조회
        result = await organization_service.get_organizations_for_chart()
        
        logger.info("기관 목록 조회 API 호출 성공")
        return result
        
    except Exception as e:
        logger.error(f"기관 목록 조회 API 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )
    
@router.get("/{name}/categories", response_model=OrganizationCategoryResponse)
async def get_organization_categories(
    name: str,
    organization_service: OrganizationService = Depends(get_organization_service)
):
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
    try:
        # Service 레이어에서 특정 기관의 카테고리별 비율 데이터 조회
        result = await organization_service.get_organization_categories_for_chart(name)
        
        logger.info(f"기관 '{name}' 카테고리 목록 조회 API 호출 성공")
        return result
        
    except Exception as e:
        logger.error(f"기관 '{name}' 카테고리 목록 조회 API 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )

@router.get("/{name}/icon", response_model=OrganizationIconResponse)
async def get_organization_icon(
    name: str,
    organization_service: OrganizationService = Depends(get_organization_service)
):
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
    try:
        # Service 레이어에서 기관 아이콘 데이터 조회
        result = await organization_service.get_organization_icon(name)
        
        logger.info(f"기관 '{name}' 아이콘 조회 API 호출 성공")
        return result
        
    except OrganizationServiceException as e:
        logger.error(f"기관 '{name}' 아이콘 조회 API 오류: {e.message}")
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"기관 '{name}' 아이콘 조회 API 예상치 못한 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )

@router.get("/{name}/wordcloud", response_model=Union[WordCloudResponse, EmptyWordCloudResponse])
async def get_organization_wordcloud(
    name: str,
    organization_service: OrganizationService = Depends(get_organization_service)
):
    """
    기관 워드클라우드 조회
    
    기관별 워드클라우드 데이터를 조회합니다.
    최근 2개년의 워드클라우드 데이터를 연도별로 제공하며,
    데이터가 없는 경우 기본 워드클라우드("죄송합니다")를 반환합니다.
    
    Args:
        name (str): 조회할 기관의 이름 (예: "국회")
        organization_service: 기관 서비스 의존성 주입
        
    Returns:
        Union[WordCloudResponse, EmptyWordCloudResponse]: 
            - WordCloudResponse: 연도별 워드클라우드 데이터
            - EmptyWordCloudResponse: 데이터 없는 경우 기본 워드클라우드
        
    Raises:
        HTTPException: 서버 내부 오류 발생 시 500 상태 코드 반환
        
    Example:
        GET /api/organizations/국회/wordcloud
    """
    try:
        # Service 레이어에서 기관 워드클라우드 데이터 조회
        result = await organization_service.get_organization_wordcloud(name)
        
        logger.info(f"기관 '{name}' 워드클라우드 조회 API 호출 성공")
        return result
        
    except Exception as e:
        logger.error(f"기관 '{name}' 워드클라우드 조회 API 오류: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="서버 내부 오류가 발생했습니다."
        )