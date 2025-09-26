from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Dict, List, Any, Literal, ClassVar
from datetime import datetime, date, timedelta
from enum import Enum

from app.F6_schemas.base import BaseSchema, BaseResponse, PaginationInfo, Message



# ==============================
# 크롤링 모드 Enum
# ==============================
class OrgCrawlMode(str, Enum):
    full = "full"
    partial = "partial"

# ==============================
# NLP 서버 상태 Enum
# ==============================
class NLPServerStatus(str, Enum):
    RUNNING = "RUNNING"
    ERROR = "ERROR"
    STOPPED = "STOPPED"


# ==============================
# 기관 영어 이름
# ==============================
ORG_NAME_MAP = {
    "국회": "National Assembly",
    "교육부": "Ministry of Education",
    "고용노동부": "Ministry of Employment and Labor",
    "문화체육관광부": "Ministry of Culture, Sports and Tourism",
    "여성가족부": "Ministry of Gender Equality and Family",
}

# ==============================
# 크롤링 요청 시 세밀 제어 가능 필터
# ==============================

# 보도자료
class OrgPressReleaseCrawlOptions(BaseSchema):
    mode: OrgCrawlMode = Field(default=OrgCrawlMode.full, description="크롤링 모드: full / partial")
    organizations: Optional[List[str]] = Field(default=None, description="특정 기관 필터(None이면 전체")
    start_date: Optional[date] = Field(default_factory=lambda: date.today() - timedelta(days=1), description="크롤링 시작일 (기본: 오늘 -1)")
    end_date: Optional[date] = Field(default_factory=date.today, description="크롤링 종료일 (기본: 오늘)")

    @field_validator("organizations", mode="before")
    @classmethod 
    def empty_list_to_none(cls, v: Any) -> Optional[List[str]]: 
        if isinstance(v, list) and not v: # v가 리스트 타입이고 비어있으면 
            return None 
        return v
    
    @field_validator("end_date")
    @classmethod 
    def validate_dates(cls, v: date, info: Dict[str, Any]) -> date:
        start_date = info.data.get("start_date")
        if start_date and v and start_date > v: 
            raise ValueError("start_date는 end_date보다 작거나 같아야 합니다.")
        return v
    

# 정책뉴스
class OrgPolicyNewsCrawlOptions(BaseSchema):
    mode: OrgCrawlMode = Field(default=OrgCrawlMode.full, description="크롤링 모드: full / partial")
    organizations: Optional[List[str]] = Field(default=None, description="특정 기관 필터(None이면 전체")
    start_date: Optional[date] = Field(default_factory=lambda: date.today() - timedelta(days=1), description="크롤링 시작일 (기본: 오늘 -1)")
    end_date: Optional[date] = Field(default_factory=date.today, description="크롤링 종료일 (기본: 오늘)")

    @field_validator("organizations", mode="before")
    @classmethod 
    def empty_list_to_none(cls, v: Any) -> Optional[List[str]]: 
        if isinstance(v, list) and not v: # v가 리스트 타입이고 비어있으면 
            return None 
        return v
    
    @field_validator("end_date")
    @classmethod 
    def validate_dates(cls, v: date, info: Dict[str, Any]) -> date:
        start_date = info.data.get("start_date")
        if start_date and v and start_date > v: 
            raise ValueError("start_date는 end_date보다 작거나 같아야 합니다.")
        return v


# 정책자료 - 통합용
class OrgCrawlPolicyMaterialsOptions(BaseSchema):
    mode: OrgCrawlMode = Field(default=OrgCrawlMode.full, description="크롤링 모드: full / partial")
    categories: Optional[List[str]] = Field(default=None, description="특정 기관 필터(None이면 전체")
    start_date: Optional[date] = Field(default_factory=lambda: date.today() - timedelta(days=1), description="크롤링 시작일 (기본: 오늘 -1)")
    end_date: Optional[date] = Field(default_factory=date.today, description="크롤링 종료일 (기본: 오늘)")

    @field_validator("categories", mode="before")
    @classmethod 
    def empty_list_to_none(cls, v: Any) -> Optional[List[str]]: 
        if isinstance(v, list) and not v: # v가 리스트 타입이고 비어있으면 
            return None 
        return v
    
    @field_validator("end_date")
    @classmethod 
    def validate_dates(cls, v: date, info: Dict[str, Any]) -> date:
        start_date = info.data.get("start_date")
        if start_date and v and start_date > v: 
            raise ValueError("start_date는 end_date보다 작거나 같아야 합니다.")
        return v
    

# ==============================
# [크롤링 task_id 반환] 
# ==============================
class OrgCrawlTriggerTaskResponse(BaseResponse):
    success: bool = True 
    task_id: Optional[str|None] = None
    message: Optional[str] = None


# ==============================
# [KoreaGovOrgPressReleaseSelectors] 
# ==============================
class KoreaGovOrgPressReleaseSelectors(BaseSchema):
        """
        대한민국 정책브리핑 보도자료 목록 페이지에서
        각 항목을 파싱하기 위한 CSS 셀렉터 상수 모음
        """

        BASE_URL : ClassVar[str] = "https://www.korea.kr/briefing/pressReleaseList.do"

        LIST_ITEM : ClassVar[str] = "div.list_type ul li"
        TITLE : ClassVar[str] = "a span.text strong"
        LINK : ClassVar[str] = "a"
        DATE : ClassVar[str] = "a span.source span:first-child"
        ORG : ClassVar[str] = "a span.source span:last-child"

        # ----------------
        # CSS 선택자 요약
        # ----------------
        """
        :first-child   → 형제 요소 중 첫 번째 자식 선택 (== :nth-child(1))
        :last-child    → 형제 요소 중 마지막 자식 선택
        :nth-child(n)  → 형제 요소 중 n번째 자식 선택
        """

# ==============================
# [KoreaGovOrgPolicyNewsSelectors] 
# ==============================
# 크롤링 팁
# 해당 사이트 개발자 모드 -> elements -> copy -> selector

# ----------------
# 정책뉴스 1차 크롤링
# ----------------
class KoreaGovOrgPolicyNewsSelectors(BaseSchema):
        """
        대한민국 정책브리핑 보도자료 목록 페이지에서
        각 항목을 파싱하기 위한 CSS 셀렉터 상수 모음
        """
    
        # ----------------
        # 정책뉴스 목록 페이지 기본 URL
        # ----------------
        BASE_URL : ClassVar[str] = "https://www.korea.kr/news/policyNewsList.do"

        # ----------------
        # 정책뉴스 항목 리스트
        # ----------------
        LIST_ITEM : ClassVar[str] = "div.list_type ul li"
        """
        <div class="list_type">
            <ul>
                <li> ... </li>
                <li> ... </li>
                <li> ... </li>
            </ul>
        </div>
        """
    
        # ----------------
        # 정책뉴스 제목
        # ----------------
        TITLE : ClassVar[str] = "a span.text strong"
        """
        <a href="...">
            <span class="text">
                <strong>제목 텍스트</strong>
            </span>
        </a>
        """
    
        # ----------------
        # 정책뉴스 링크(상세 페이지 URL)
        # ----------------
        LINK : ClassVar[str] = "a"
        """
        <li>
            <a href="/news/...">
                ...
            </a>
        </li>
        """

    
        # ----------------
        # 정책뉴스 발행일
        # ----------------
        DATE : ClassVar[str] = "a span.source span:first-child"
        """
        <a href="...">
            <span class="source">
                <span>2025-09-07</span>    <-- 첫 번째 span (발행일)
                <span>기관명</span>
            </span>
        </a>
        """
    
        # ----------------
        # 정책뉴스 기관명
        # ----------------
        ORG : ClassVar[str] = "a span.source span:last-child"
        """
        <a href="...">
            <span class="source">
                <span>2025-09-07</span>
                <span>기관명</span>        <-- 마지막 span (기관명)
            </span>
        </a>
        """

        # ----------------
        # CSS 선택자 요약
        # ----------------
        """
        :first-child   → 형제 요소 중 첫 번째 자식 선택 (== :nth-child(1))
        :last-child    → 형제 요소 중 마지막 자식 선택
        :nth-child(n)  → 형제 요소 중 n번째 자식 선택
        """

# ----------------
# 정책뉴스 2차 크롤링
# ----------------
class KoreaGovOrgPolicyNewsDetailSelectors(BaseSchema):
    """
    정책뉴스 상세 페이지에서 본문 텍스트를 파싱하기 위한 CSS 셀렉터
    """
    # 본문 전체 컨테이너
    ARTICLE_BODY : ClassVar[str] = "div.view_cont[itemprop='articleBody']"

    # 본문 문단 <p> 태그 선택
    PARAGRAPHS : ClassVar[str] = "p"

# ==============================
# [정책자료]
# ==============================
