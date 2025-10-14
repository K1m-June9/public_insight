import logging

from typing import Union
from pathlib import Path
from datetime import date
import random

from app.F3_repositories.organization import OrganizationRepository
from app.F6_schemas.organization import (
    OrganizationListResponse, 
    OrganizationListData, 
    OrganizationListItem, 
    OrganizationCategoryData, 
    OrganizationCategoryResponse, 
    OrganizationInfo,
    CategoryItem,
    OrganizationIconData,
    OrganizationWithIcon,
    OrganizationIconResponse,
    WordCloudKeywordItem,
    WordCloudData,
    WordCloudResponse,
    OrganizationStats, 
    OrganizationSummaryData, 
    OrganizationSummaryResponse
    )
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

WORDCLOUD_COLORS = ["#1e40af", "#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe"]

# 커스텀 예외 클래스
# class OrganizationServiceException(Exception):
#     def __init__(self, code: str, message: str, status_code: int):
#         self.code = code
#         self.message = message
#         self.status_code = status_code
#         super().__init__(message)

class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository):
        self.organization_repo = organization_repo

    def _create_icon_url(self, icon_path: str | None) -> str:
        if not icon_path:
            return ""
        return f"{Settings.STATIC_FILES_URL}/organization_icon/{icon_path}"

    def _calculate_scaled_percentages(self, items: list, count_key: str, scale_to: float = 95.0) -> list:
        total_count = sum(item[count_key] for item in items)
        if total_count == 0:
            return [] # 피드가 전혀 없는 경우 빈 리스트 반환

        for item in items:
            percentage = (item[count_key] / total_count) * scale_to
            item['percentage'] = round(percentage, 1)
        
        current_sum = sum(item['percentage'] for item in items)
        if current_sum != scale_to and items:
            adjustment = scale_to - current_sum
            items[0]['percentage'] = round(items[0]['percentage'] + adjustment, 1)
            
        return items
    
    # 메인페이지 원형 그래프용 기관 목록과 비율 조회 메서드
    # 입력: 없음
    # 반환: 
    #   OrganizationListResponse - 기관 목록과 각 기관별 비율이 포함된 응답 객체
    # 설명: 
    #   활성화된 기관들의 피드 개수를 기반으로 비율을 계산하여 95%로 스케일링
    #   나머지 5%는 "기타" 항목으로 고정 할당하여 총 100% 구성
    #   소수점 보정을 통해 정확히 100%가 되도록 보장
    #   원형 그래프 렌더링을 위한 완전한 데이터 제공
    async def get_organizations_for_chart(self) -> Union[OrganizationListResponse, ErrorResponse]:
        try:
            orgs_with_counts = await self.organization_repo.get_organizations_with_feed_counts()
            if not orgs_with_counts:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.ORGANIZATION_NOT_FOUND
                    )
                )
            
            organization_items = [
                OrganizationListItem(
                    id=org["organization_id"], 
                    name=org["organization_name"], 
                    feed_count=org["feed_count"]
                ) 
                for org in orgs_with_counts
            ]
            
            response_data = OrganizationListData(organizations=organization_items)

            return OrganizationListResponse(success=True, data=response_data)
        
        except Exception as e:
            logger.error(f"Error in get_organizations_for_chart: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
        
    # 특정 기관의 카테고리별 비율 조회 메서드 (원형 그래프용)
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   OrganizationCategoryResponse - 기관 정보와 카테고리별 비율이 포함된 응답 객체
    # 설명: 
    #   특정 기관의 활성화된 카테고리들의 피드 개수를 기반으로 비율을 계산하여 95%로 스케일링
    #   나머지 5%는 "기타" 항목으로 고정 할당하여 총 100% 구성
    #   소수점 보정을 통해 정확히 100%가 되도록 보장
    #   기관별 카테고리 원형 그래프 렌더링을 위한 완전한 데이터 제공
    async def get_organization_categories_for_chart(self, org_name: str) -> Union[OrganizationCategoryResponse, ErrorResponse]:
        try:
            cats_with_counts = await self.organization_repo.get_categories_with_feed_counts_by_org_name(org_name)
            if not cats_with_counts:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.CATEGORY_NOT_FOUND
                    )
                )

            organization_info = OrganizationInfo(id=cats_with_counts[0]["organization_id"], name=cats_with_counts[0]["organization_name"])
            
            processed_cats = self._calculate_scaled_percentages(cats_with_counts, 'feed_count')
            if not processed_cats:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.CATEGORY_FEED_NOT_FOUND
                    )
                )
            
            #기관 페이지 수정으로 인한 feed_count를 추가하여 전달
            category_items = [CategoryItem(
                id=cat["category_id"], 
                name=cat["category_name"], 
                percentage=cat["percentage"],
                feed_count=cat["feed_count"]
                ) for cat in processed_cats]
            category_items.append(CategoryItem(id=999, name="기타", percentage=5.0, feed_count=0)) #아 이거 기타 언제 제대로 바꿔야하는데 아직 미정 시발ㅋㅋ

            total_percentage = sum(item.percentage for item in category_items)
            response_data = OrganizationCategoryData(organization=organization_info, categories=category_items, total_percentage=round(total_percentage, 1))
            
            return OrganizationCategoryResponse(success=True,data=response_data)
        except Exception as e:
            logger.error(f"Error in get_organization_categories_for_chart for {org_name}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    #message=Message.INTERNAL_ERROR
                    message = f"{org_name}:{e}"
                )
            )
        

    # 기관 아이콘 조회 메서드
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   OrganizationIconResponse - 기관 정보와 Base64 인코딩된 아이콘이 포함된 응답 객체
    # 설명: 
    #   특정 기관의 아이콘을 Base64 형식으로 변환하여 반환
    #   데이터베이스에 저장된 icon_path를 실제 파일 시스템 경로로 변환
    #   파일 읽기 및 Base64 인코딩을 통해 브라우저에서 직접 사용 가능한 Data URL 제공
    #   기관이 존재하지 않으면 404, 파일 오류 시 500 예외 발생
    async def get_organization_icon(self, org_name: str) -> Union[OrganizationIconResponse, ErrorResponse]:
        try:
            organization_data = await self.organization_repo.get_organization_by_name(org_name)
            if not organization_data:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.ORGANIZATION_NOT_FOUND
                    )
                )

            icon_url = self._create_icon_url(organization_data["icon_path"])
            
            organization_with_icon = OrganizationWithIcon(
                id=organization_data["id"],
                name=organization_data["name"],
                website_url=organization_data["website_url"] or "",
                icon=icon_url
            )
            
            return OrganizationIconResponse(success=True, data=OrganizationIconData(organization=organization_with_icon))
        except Exception as e:
            logger.error(f"Error in get_organization_icon for {org_name}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.ICON_UPLOADS_FAIL
                )
            )
        
    async def get_organization_summary(self, org_name: str) -> Union[OrganizationSummaryResponse, ErrorResponse]:
        """
        기관 상세 페이지 헤더에 필요한 요약 정보와 통계를 제공
        """
        try:
            summary_data = await self.organization_repo.get_organization_summary_by_name(org_name)

            if not summary_data:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.ORGANIZATION_NOT_FOUND))

            # 통계 데이터 객체 생성
            stats = OrganizationStats(
                documents=summary_data['total_documents'],
                views=summary_data['total_views'],
                satisfaction=float(summary_data['average_satisfaction'])
            )
            
            # 최종 응답 데이터 객체 생성
            response_data = OrganizationSummaryData(
                id=summary_data['id'],
                name=summary_data['name'],
                description=summary_data['description'] or "",
                website_url=summary_data['website_url'],
                stats=stats
            )

            return OrganizationSummaryResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error in get_organization_summary for {org_name}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))
        
    async def get_organization_wordcloud(self, org_name: str) -> Union[WordCloudResponse, ErrorResponse]:
        """
        기관별 주요 키워드(워드클라우드용) 데이터를 조회
        score에 따라 글자 크기와 굵기를 동적으로 계산하고, 색상은 랜덤으로 할당
        """
        try:
            # 1. 리포지토리에서 상위 14개 키워드 객체 목록을 가져옴
            keywords = await self.organization_repo.get_top_keywords_by_org_name(org_name, limit=14)

            # 기관 정보 조회를 위해, 키워드가 없더라도 기관 자체는 있는지 확인
            org_info_data = await self.organization_repo.get_organization_by_name(org_name)
            if not org_info_data:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.ORGANIZATION_NOT_FOUND))
            
            organization_info = OrganizationInfo(id=org_info_data['id'], name=org_info_data['name'])

            # 2. 키워드 목록을 WordCloudKeywordItem 스키마로 변환
            keyword_items = []
            if keywords:
                # 점수 범위를 계산하여 글자 크기/굵기를 정규화하기 위함
                scores = [k.score for k in keywords]
                min_score, max_score = min(scores), max(scores)

                for keyword in keywords:
                    # 점수(score)를 UI 속성(size, weight)으로 변환
                    size = self._calculate_font_size(keyword.score, min_score, max_score)
                    weight = 600 if keyword.score >= (max_score * 0.7) else 500

                    keyword_item = WordCloudKeywordItem(
                        text=keyword.keyword,
                        size=size,
                        color=random.choice(WORDCLOUD_COLORS), # 색상 랜덤 할당
                        weight=weight
                    )
                    keyword_items.append(keyword_item)
            
            # 3. 최종 응답 데이터 구성
            response_data = WordCloudData(
                organization=organization_info,
                keywords=keyword_items
            )
            
            return WordCloudResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"Error in get_organization_wordcloud for {org_name}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))

    # --- 💡 3. 동적 계산을 위한 헬퍼 함수 추가 💡 ---
    def _calculate_font_size(self, score: float, min_score: float, max_score: float) -> int:
        """점수를 기반으로 10px ~ 32px 사이의 폰트 크기를 계산"""
        if max_score == min_score: # 모든 점수가 같을 경우 중간 크기 반환
            return 21
        
        # min-max normalization (점수를 0~1 사이 값으로 정규화)
        normalized_score = (score - min_score) / (max_score - min_score)
        
        # 폰트 크기 범위 설정
        min_font_size = 10
        max_font_size = 32
        
        # 정규화된 점수를 폰트 크기 범위에 맞게 스케일링
        font_size = min_font_size + normalized_score * (max_font_size - min_font_size)
        return round(font_size)