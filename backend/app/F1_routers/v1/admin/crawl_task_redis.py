from fastapi import APIRouter, Depends

from app.F5_core.redis import CrawlTaskRedisService
from app.F5_core.logging_decorator import log_event_detailed
from app.F5_core.dependencies import get_admin_crawl_task_redis_service 

from app.F6_schemas.admin.crawl_task_redis import (
    CrawlTaskResponse, 
    CrawlTaskRequest, 
    CrawlAllTaskResponse, 
)

from app.F6_schemas.base import ErrorResponse, ErrorCode, SuccessResponse

router = APIRouter(tags=["Admin- Redis Task"], prefix="/redis-task")

# ==================================================
# Redis Teask API
# ==================================================

# --------------------
# [모두 조회]
# --------------------
@router.get("/result", response_model=CrawlAllTaskResponse)
@log_event_detailed(action="get_all_crawl_task_status", category=["ADMIN", "Crawler"])
async def get_all_crawl_results(
    service: CrawlTaskRedisService = Depends(get_admin_crawl_task_redis_service)
):
    result = await service.get_all_task_info()
    return result


# --------------------
# [검색 조회]
# --------------------
@router.post("/result", response_model=CrawlTaskResponse)
@log_event_detailed(action="get_crawl_task_status", category=["ADMIN", "Crawler"])
async def get_crawl_result(
    request_body: CrawlTaskRequest,
    service: CrawlTaskRedisService = Depends(get_admin_crawl_task_redis_service)
):
    result = await service.get_task_info(request_body.task_id)
    return result


# --------------------
# [삭제]
# --------------------
@router.delete("/result", response_model=SuccessResponse)
@log_event_detailed(action="delete_non_in_progress_tasks", category=["ADMIN", "Crawler"])
async def delete_non_in_progress_tasks(
    service: CrawlTaskRedisService = Depends(get_admin_crawl_task_redis_service)
):
    result = await service.delete_all_except_in_progress()
    return result