from fastapi import APIRouter, Depends, BackgroundTasks, status 
from fastapi.responses import JSONResponse

from app.F2_services.admin.org_crawler import OrgCrawlerTriggerAdminService

from app.F5_core.logging_decorator import log_event_detailed
from app.F5_core.dependencies import get_admin_org_crawler_trigger_service

from app.F6_schemas.admin.org_crawler import (
    OrgPressReleaseCrawlOptions, 
    OrgCrawlTriggerTaskResponse,
    OrgPolicyNewsCrawlOptions,
)

from app.F6_schemas.admin.crawl_task_redis import JobName


from app.F6_schemas.base import ErrorResponse, ErrorCode, Message

router = APIRouter(tags=["Admin-Org Crawler"], prefix="/org-crawler")

# ==================================================
# Crawler Trigger
# ==================================================

# -------------
# [보도자료 크롤링]
# -------------
@router.post("/trigger/press-release", status_code=status.HTTP_202_ACCEPTED, response_model=OrgCrawlTriggerTaskResponse)
@log_event_detailed(action="trigger_org_press_release_crawl", category=["ADMIN", "Crawler"])
async def trigger_org_press_release_crawl(
    options: OrgPressReleaseCrawlOptions,
    tasks: BackgroundTasks,
    service: OrgCrawlerTriggerAdminService = Depends(get_admin_org_crawler_trigger_service),
):
    """
    관리자가 수동으로 보도자료 크롤링을 시작하는 엔드포인트
    - 크롤링은 백그라운드에서 진행
    - Redis에 작업 상태 기록
    """
    task_id = await service.create_crawl_task(JobName.ORG_PRESS_RELEASE)
    tasks.add_task(service.run_manual_press_release_crawl, tasks, task_id, options)

    return OrgCrawlTriggerTaskResponse(
        task_id=task_id,
        message=Message.SUCCESS,
        success=True
    )

# -------------
# [정책뉴스 크롤링]
# -------------
@router.post("/trigger/policy-news", response_model=OrgCrawlTriggerTaskResponse)
@log_event_detailed(action="trigger_org_policy_news_crawl", category=["ADMIN", "Crawler"])
async def trigger_org_policy_news_crawl(
    options: OrgPolicyNewsCrawlOptions,
    tasks: BackgroundTasks,
    service: OrgCrawlerTriggerAdminService = Depends(get_admin_org_crawler_trigger_service),
):
    """
    관리자가 수동으로 정책뉴스 크롤링을 시작하는 엔드포인트
    - 크롤링은 백그라운드에서 진행
    - Redis에 작업 상태 기록
    """
    task_id = await service.create_crawl_task(JobName.ORG_POLICY_NEWS)
    tasks.add_task(service.run_manual_policy_news_crawl, tasks, task_id, options)
    
    return OrgCrawlTriggerTaskResponse(
        task_id=task_id,
        message=Message.SUCCESS,
        success=True
    )


