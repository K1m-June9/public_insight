import logging

from typing import Union
from pathlib import Path
from datetime import date

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
    WordCloudByYear,
    WordCloudData,
    WordCloudPeriod,
    WordItem,
    WordCloudResponse,
    EmptyWordCloud,
    EmptyWordCloudData,
    EmptyWordCloudResponse,
    OrganizationStats, 
    OrganizationSummaryData, 
    OrganizationSummaryResponse
    )
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

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
            # 피드 개수를 기반으로 하여 95% 스케일링 -> 5%=기타
            processed_orgs = self._calculate_scaled_percentages(orgs_with_counts, 'feed_count')
            if not processed_orgs: # 모든 기관의 피드 개수가 0인 경우
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.ORGANIZATION_FEED_NOT_FOUND
                    )
                )

            organization_items = [OrganizationListItem(id=org["organization_id"], name=org["organization_name"], percentage=org["percentage"]) for org in processed_orgs]
            organization_items.append(OrganizationListItem(id=999, name="기타", percentage=5.0))
            
            total_percentage = sum(item.percentage for item in organization_items)
            response_data = OrganizationListData(organizations=organization_items, total_percentage=round(total_percentage, 1))
            
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
        

    # 기관 워드클라우드 조회 메서드
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   WordCloudResponse - 성공 시 연도별 워드클라우드 데이터
    #   EmptyWordCloudResponse - 데이터 없는 경우 기본 워드클라우드
    # 설명: 
    #   특정 기관의 최근 2개년 워드클라우드 데이터를 조회하여 스키마에 맞게 변환
    #   Repository에서 JSON 형태의 cloud_data를 WordItem 리스트로 변환
    #   value는 반올림 처리하여 int 타입으로 변환
    #   데이터가 없는 경우 "죄송합니다" 기본 워드클라우드 반환
    async def get_organization_wordcloud(self, org_name: str) -> Union[WordCloudResponse, EmptyWordCloudResponse, ErrorResponse]:
        try:
            wordcloud_data = await self.organization_repo.get_organization_wordclouds_by_name(org_name, date.today())
            
            # 워드클라우드 데이터가 없는 경우 (EmptyWordCloudResponse 반환)
            if not wordcloud_data:
                org = await self.organization_repo.get_organization_by_name(org_name)
                org_id = org['id'] if org else 0
                
                empty_data = EmptyWordCloudData(
                    organization=OrganizationInfo(id=org_id, name=org_name),
                    wordcloud=EmptyWordCloud(words=[WordItem(text="죄송합니다", value=100)]) # 워드 클라우드 데이터가 없는 경우에 사용(사실상 기본값)
                )
                return EmptyWordCloudResponse(success=True, data=empty_data)

            organization_info = OrganizationInfo(id=wordcloud_data[0]["organization_id"], name=wordcloud_data[0]["organization_name"])
            
            wordclouds_by_year = []
            for item in wordcloud_data:
                word_items = [WordItem(text=d["text"], value=round(d["value"])) for d in item["cloud_data"]]
                wordclouds_by_year.append(WordCloudByYear(
                    year=item["period_start"].year,
                    words=word_items,
                    period=WordCloudPeriod(start_date=item["period_start"], end_date=item["period_end"]),
                    generated_at=item["created_at"]
                ))
            
            return WordCloudResponse(
                success=True,
                data=WordCloudData(
                    organization=organization_info,
                    wordclouds=wordclouds_by_year
                )
            )
        except Exception as e:
            logger.error(f"Error in get_organization_wordcloud for {org_name}: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
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