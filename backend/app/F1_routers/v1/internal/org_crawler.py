from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks, status

from app.F2_services.internal.org_crawler import OrgCrawlerDataReceiverService
from app.F3_repositories.internal.org_crawler import OrgCrawlerRepository
from app.F5_core.config import settings
from app.F5_core.dependencies import get_crawler_org_data_receiver_service
from app.F6_schemas.internal.org_korea_dot_kr import (
    OrgPressReleaseCrawlRequest,
    OrgPolicyNewsCrawlRequest,
)


# --- API 문서에 노출되지 않도록 설정 ---
# -- 배포 --
# router = APIRouter(tags=["Internal - Crawler Receiver"], include_in_schema=False)

# -- 테스트 --
router = APIRouter(tags=["Internal-Crawler Receiver"])


# --- API 키 인증을 위한 의존성 함수 ---
async def verify_api_key(x_api_key: str = Header(..., description="내부 크롤러 인증을 위한 API 키")):
    if x_api_key != settings.CRAWLER_API_KEY:
        # 오류 발생시 어떻게 처리할지는 고민중 
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")

# --- 보도자료 크롤링 데이터 수신 엔드포인트 ---
@router.post("/crawl-request/korea-gov-press-release", status_code=status.HTTP_202_ACCEPTED)
async def receive_korea_gov_press_release(
    request_data: OrgPressReleaseCrawlRequest,
    tasks: BackgroundTasks,
    service: OrgCrawlerDataReceiverService = Depends(get_crawler_org_data_receiver_service),
    api_key: str = Depends(verify_api_key)
):
    """
    '대한민국 정책브리핑' 보도자료 크롤러로부터 수집된 데이터를 받아
    백그라운드 처리를 시작합니다.
    """

    result = await service.process_press_release_data(request_data.items, tasks)
    return result


# --- 정책뉴스 크롤링 데이터 수신 엔드포인트 ---
@router.post("/crawl-request/korea-gov-policy-news", status_code=status.HTTP_202_ACCEPTED)
async def receive_korea_gov_policy_news(
    request_data: OrgPolicyNewsCrawlRequest,
    tasks: BackgroundTasks, 
    service: OrgCrawlerDataReceiverService = Depends(get_crawler_org_data_receiver_service),
    api_key: str = Depends(verify_api_key)
):
    """
    '대한민국 정책브리핑' 정책뉴스 크롤러로부터 수집된 데이터를 받아 백그라운드 처리를 시작
    """
    result = await service.process_policy_news_data(request_data.items, tasks)
    return result 
