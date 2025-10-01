from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

from app.F6_schemas.base import BaseSchema, BaseResponse


# ==============================
# 작업명 Enum
# ==============================
class JobName(str, Enum):
    ORG_PRESS_RELEASE = "부_보도자료"
    ORG_POLICY_MATERIALS = "부_정책자료"
    ORG_POLICY_NEWS = "부_정책뉴스"



# ==============================
# 크롤링 상태 Enum
# ==============================
class TaskStatus(str, Enum):
    PENDING = "PENDING" # 보류 중
    IN_PROGRESS  = "IN_PROGRESS" # 진행 중
    COMPLETED = "COMPLETED" # 완료
    FAILED = "FAILED" # 실패



# ==============================
# 크롤링 내부 정보 result 스키마
# ==============================
class CrawlTaskResult(BaseSchema):
    job_name: Optional[JobName] = None      # 선택
    target_orgs: List[str] = Field(default_factory=list) # 선택
    total_items: int = 0                    # 선택 
    message: Optional[str] = None           # 선택


# ==============================
# [크롤링 태스크 진행 결과]
# 입력 스키마 
# ==============================
class CrawlTaskRequest(BaseSchema):
    task_id: str 


# ==============================
# [크롤링 태스크 진행 결과]
# 출력 스키마
# ==============================
class CrawlTaskData(BaseSchema):
    task_id: str 
    job_name: str 
    status: Optional[TaskStatus]
    started_at: datetime
    completed_at: Optional[datetime] = None 
    target_orgs: List[str] = Field(default_factory=list)
    total_items: int = 0 
    message: Optional[str] = None 

class CrawlAllTaskResponse(BaseResponse):
    success: bool = True
    data: List[CrawlTaskData]


class CrawlTaskResponse(BaseResponse):
    success: bool = True
    data: CrawlTaskData