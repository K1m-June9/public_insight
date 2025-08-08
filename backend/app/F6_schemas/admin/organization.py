from typing import List
from app.F6_schemas.base import BaseSchema, BaseResponse

# 기존 계획에 없던 건데 필요해서 새로 생성한 스키마(관리자 피드 리스트 확인 시 기관 확인)
#======================================================
class SimpleOrganizationItem(BaseSchema):
    """관리자 필터링용 기관 정보 (ID와 이름만 포함)"""
    id: int
    name: str

class SimpleOrganizationListResponse(BaseResponse):
    """관리자 필터링용 기관 목록 응답"""
    data: List[SimpleOrganizationItem]

#======================================================