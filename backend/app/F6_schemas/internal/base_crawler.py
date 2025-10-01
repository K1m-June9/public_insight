from pydantic import BaseModel
from typing import List, TypeVar, Generic

# 제네릭(Generic)을 사용하여 어떤 타입의 아이템이든 담을 수 있도록 함
ItemType = TypeVar('ItemType')

class BaseCrawlRequest(BaseModel, Generic[ItemType]):
    """
    모든 크롤링 요청에서 공통으로 사용할 기본 요청 본문 스키마.
    어떤 종류의 'items' 리스트든 받을 수 있습니다.
    """
    items: List[ItemType]