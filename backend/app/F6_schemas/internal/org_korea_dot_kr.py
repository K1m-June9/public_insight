from pydantic import BaseModel, HttpUrl
from datetime import datetime
from .base_crawler import BaseCrawlRequest



# ==============================
# 보도자료
# ==============================
class OrgPressReleaseItem(BaseModel):
    """
    '대한민국 정책브리핑' 보도자료(Press Release) 크롤러가 수집한
    개별 게시물의 메타데이터 스키마
    """
    organization_name: str
    title: str
    published_date: datetime
    source_url: HttpUrl
    # pdf_url은 2차 크롤링으로 서버에서 찾으므로, 크롤러는 보내지 않음


class OrgPressReleaseCrawlRequest(BaseCrawlRequest[OrgPressReleaseItem]):
    """
    '대한민국 정책브리핑' 보도자료 크롤링 요청 본문.
    """
    pass # BaseCrawlRequest의 구조를 그대로 상속


# ==============================
# 정책뉴스
# ==============================
class OrgPolicyNewsItem(BaseModel):
    """
    '대한민국 정책 브리핑' 정책뉴스 크롤러가 수집한
    개별 게시물의 메타데이터 스키마
    """
    organization_name: str
    title: str
    published_date: datetime
    source_url: HttpUrl
    # pdf_url은 2차 크롤링으로 서버에서 찾으므로, 크롤러는 보내지 않음


class OrgPolicyNewsCrawlRequest(BaseCrawlRequest[OrgPolicyNewsItem]):
    """
    '대한민국 정책브리핑' 정책뉴스 크롤링 요청 본문.
    """
    pass # BaseCrawlRequest의 구조를 그대로 상속


# ==============================
# 정책자료
# ==============================
class OrgPolicyMaterialsItem(BaseModel):
    """
    [공통]
    기관의 정책자료 크롤러가 수집한 개별 게시물의 메타데이터 스미카
    """
    category: str 
    title: str 
    published_date: datetime 
    source_url: HttpUrl 

class OrgPolicyMaterialsCrawlRequest(BaseCrawlRequest[OrgPolicyMaterialsItem]):
    """
    정책자료 크롤링 요청 본문
    """
    pass 
