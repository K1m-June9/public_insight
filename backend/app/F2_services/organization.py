import base64
import os
import logging

from typing import List, Union
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
    EmptyWordCloudResponse
    )
from app.F6_schemas.base import ErrorCode, Message

logger = logging.getLogger(__name__)

# 커스텀 예외 클래스
class OrganizationServiceException(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class OrganizationService:
    def __init__(self, organization_repo: OrganizationRepository):
        self.organization_repo = organization_repo
    
    # 메인페이지 원형 그래프용 기관 목록과 비율 조회 메서드
    # 입력: 없음
    # 반환: 
    #   OrganizationListResponse - 기관 목록과 각 기관별 비율이 포함된 응답 객체
    # 설명: 
    #   활성화된 기관들의 피드 개수를 기반으로 비율을 계산하여 95%로 스케일링
    #   나머지 5%는 "기타" 항목으로 고정 할당하여 총 100% 구성
    #   소수점 보정을 통해 정확히 100%가 되도록 보장
    #   원형 그래프 렌더링을 위한 완전한 데이터 제공
    async def get_organizations_for_chart(self) -> OrganizationListResponse:
        try:
            # Repository에서 활성화된 기관과 피드 개수 조회
            organizations_data = await self.organization_repo.get_organizations_with_feed_counts()
            
            # 빈 데이터 검증 - 활성화된 기관이 없는 경우 서버 오류
            if not organizations_data:
                logger.error("활성화된 기관 데이터가 없습니다")
                raise Exception("활성화된 기관 데이터를 찾을 수 없습니다")
            
            # 전체 피드 개수 계산
            total_feeds = sum(org["feed_count"] for org in organizations_data)
            
            # 모든 기관의 피드 개수가 0인 경우 처리
            if total_feeds == 0:
                logger.error("모든 기관의 피드 개수가 0입니다")
                raise Exception("피드 데이터가 존재하지 않습니다")
            
            # 각 기관별 비율 계산 (95% 기준으로 스케일링)
            organization_items = []
            calculated_percentages = []
            
            for org in organizations_data:
                # 개별 기관 비율 = (해당 기관 피드 수 / 전체 피드 수) * 95
                percentage = (org["feed_count"] / total_feeds) * 95.0
                calculated_percentages.append(percentage)
                
                organization_items.append(OrganizationListItem(
                    id=org["organization_id"],
                    name=org["organization_name"],
                    percentage=round(percentage, 1)
                ))
            
            # 95% 스케일링 후 소수점 보정
            # 반올림으로 인한 오차를 첫 번째 기관에서 보정
            current_sum = sum(round(p, 1) for p in calculated_percentages)
            target_sum = 95.0
            
            if current_sum != target_sum:
                adjustment = target_sum - current_sum
                organization_items[0].percentage = round(organization_items[0].percentage + adjustment, 1)
                logger.info(f"비율 보정 적용: {adjustment}% 조정")
            
            # "기타" 항목 추가 (5% 고정 할당)
            organization_items.append(OrganizationListItem(
                id=999,
                name="기타",
                percentage=5.0
            ))
            
            # 최종 검증 - 총합이 100%인지 확인
            total_percentage = sum(item.percentage for item in organization_items)
            
            # 응답 데이터 구성
            response_data = OrganizationListData(
                organizations=organization_items,
                total_percentage=round(total_percentage, 1)
            )
            
            logger.info(f"기관별 비율 계산 완료 - 총 {len(organization_items)}개 기관, 총합 {total_percentage}%")
            
            return OrganizationListResponse(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"기관 목록 조회 중 오류 발생: {str(e)}")
            raise Exception(f"기관 목록 조회에 실패했습니다: {str(e)}")
        
        
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
    async def get_organization_categories_for_chart(self, org_name: str) -> OrganizationCategoryResponse:
        try:
            # Repository에서 특정 기관의 카테고리와 피드 개수 조회
            result = await self.organization_repo.get_categories_with_feed_counts_by_org_name(org_name)
            
            # 데이터 검증 - 기관이 없거나 활성화된 카테고리가 없는 경우 예외 발생
            if not result:
                logger.error(f"기관 '{org_name}'을 찾을 수 없거나 활성화된 카테고리가 없습니다")
                raise Exception(f"기관 '{org_name}'을 찾을 수 없거나 활성화된 카테고리가 없습니다")
            
            # 기관 정보 추출
            organization_info = OrganizationInfo(
                id=result["organization"]["id"],
                name=result["organization"]["name"]
            )
            
            # 전체 피드 개수 계산
            categories_data = result["categories"]
            total_feeds = sum(cat["feed_count"] for cat in categories_data)
            
            # 모든 카테고리의 피드 개수가 0인 경우 예외 발생
            if total_feeds == 0:
                logger.error(f"기관 '{org_name}'의 모든 카테고리에 피드가 없습니다")
                raise Exception(f"기관 '{org_name}'의 카테고리에 피드 데이터가 존재하지 않습니다")
            
            # 각 카테고리별 비율 계산 (95% 기준으로 스케일링)
            category_items = []
            calculated_percentages = []
            
            for cat in categories_data:
                # 개별 카테고리 비율 = (해당 카테고리 피드 수 / 전체 피드 수) * 95
                percentage = (cat["feed_count"] / total_feeds) * 95.0
                calculated_percentages.append(percentage)
                
                category_items.append(CategoryItem(
                    id=cat["category_id"],
                    name=cat["category_name"],
                    percentage=round(percentage, 1)
                ))
            
            # 95% 스케일링 후 소수점 보정
            # 반올림으로 인한 오차를 첫 번째 카테고리에서 보정
            current_sum = sum(round(p, 1) for p in calculated_percentages)
            target_sum = 95.0
            
            if current_sum != target_sum:
                adjustment = target_sum - current_sum
                category_items[0].percentage = round(category_items[0].percentage + adjustment, 1)
                logger.info(f"카테고리 비율 보정 적용: {adjustment}% 조정")
            
            # "기타" 항목 추가 (5% 고정 할당)
            category_items.append(CategoryItem(
                id=999,
                name="기타",
                percentage=5.0
            ))
            
            # 최종 검증 - 총합이 100%인지 확인
            total_percentage = sum(item.percentage for item in category_items)
            
            # 응답 데이터 구성
            response_data = OrganizationCategoryData(
                organization=organization_info,
                categories=category_items,
                total_percentage=round(total_percentage, 1)
            )
            
            logger.info(f"기관 '{org_name}'의 카테고리별 비율 계산 완료 - 총 {len(category_items)}개 카테고리, 총합 {total_percentage}%")
            
            return OrganizationCategoryResponse(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"기관 '{org_name}' 카테고리 목록 조회 중 오류 발생: {str(e)}")
            raise Exception(f"기관 '{org_name}' 카테고리 목록 조회에 실패했습니다: {str(e)}")
        

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
    async def get_organization_icon(self, org_name: str) -> OrganizationIconResponse:
        try:
            # Repository에서 기관 정보 조회
            organization_data = await self.organization_repo.get_organization_by_name(org_name)
            
            # 기관이 존재하지 않는 경우 404 예외 발생
            if not organization_data:
                logger.error(f"기관 '{org_name}'을 찾을 수 없습니다")
                raise OrganizationServiceException(
                    "ORGANIZATION_NOT_FOUND",
                    "존재하지 않는 기관입니다.",
                    404
                )
            
            # 아이콘 파일 경로 구성
            # DB 저장 형식: /organization_icon/{UUID}
            # 실제 파일 경로: backend/app/organization_icon/{UUID}
            icon_path_from_db = organization_data["icon_path"]
            if not icon_path_from_db:
                logger.error(f"기관 '{org_name}'의 아이콘 경로가 설정되지 않았습니다")
                raise OrganizationServiceException(
                    "ICON_LOAD_ERROR",
                    "아이콘을 불러오는 중 오류가 발생했습니다.",
                    500
                )
            
            # 실제 파일 시스템 경로로 변환
            # /organization_icon/{UUID} → backend/app/organization_icon/{UUID}
            current_dir = Path(__file__).parent.parent  # backend/app 디렉토리
            actual_icon_path = current_dir / icon_path_from_db.lstrip('/')
            
            # 아이콘 파일을 Base64로 변환
            base64_icon = self._convert_icon_to_base64(str(actual_icon_path))
            
            # 스키마에 맞춰 응답 데이터 구성
            organization_with_icon = OrganizationWithIcon(
                id=organization_data["id"],
                name=organization_data["name"],
                website_url=organization_data["website_url"] or "",  # None인 경우 빈 문자열
                icon=base64_icon
            )
            
            response_data = OrganizationIconData(
                organization=organization_with_icon
            )
            
            logger.info(f"기관 '{org_name}' 아이콘 조회 완료")
            
            return OrganizationIconResponse(
                success=True,
                data=response_data
            )
            
        except OrganizationServiceException:
            # 이미 처리된 예외는 그대로 재발생
            raise
        except Exception as e:
            logger.error(f"기관 '{org_name}' 아이콘 조회 중 예상치 못한 오류 발생: {str(e)}")
            raise OrganizationServiceException(
                "ICON_LOAD_ERROR",
                "아이콘을 불러오는 중 오류가 발생했습니다.",
                500
            )

    # 이미지 파일을 Base64로 변환하는 내부 메서드
    # 입력: 
    #   image_path - 이미지 파일 경로 (str)
    # 반환: 
    #   Data URL 형식의 base64 인코딩된 이미지 데이터 (str)
    # 설명: 
    #   주어진 경로의 .ico 파일을 읽어서 Base64로 인코딩
    #   data:image/x-icon;base64, 형식으로 반환하여 브라우저에서 직접 사용 가능
    #   파일 읽기 실패 시 ICON_LOAD_ERROR 예외 발생
    def _convert_icon_to_base64(self, image_path: str) -> str:
        try:
            # 파일 존재 여부 확인
            if not os.path.exists(image_path):
                logger.error(f"아이콘 파일이 존재하지 않습니다: {image_path}")
                raise OrganizationServiceException(
                    "ICON_LOAD_ERROR",
                    "아이콘을 불러오는 중 오류가 발생했습니다.",
                    500
                )
            
            # 파일 읽기 및 Base64 인코딩
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_encoded = base64.b64encode(image_data).decode('utf-8')
                
            # Data URL 형식으로 반환 (.ico 파일용)
            data_url = f"data:image/x-icon;base64,{base64_encoded}"
            
            logger.info(f"아이콘 파일 Base64 변환 완료: {image_path}")
            return data_url
            
        except OrganizationServiceException:
            # 이미 처리된 예외는 그대로 재발생
            raise
        except Exception as e:
            logger.error(f"아이콘 파일 변환 중 오류 발생: {str(e)}")
            raise OrganizationServiceException(
                "ICON_LOAD_ERROR",
                "아이콘을 불러오는 중 오류가 발생했습니다.",
                500
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
    async def get_organization_wordcloud(self, org_name: str) -> Union[WordCloudResponse, EmptyWordCloudResponse]:
        try:
            # 현재 날짜 기준으로 Repository에서 워드클라우드 데이터 조회
            current_date = date.today()
            wordcloud_data = await self.organization_repo.get_organization_wordclouds_by_name(
                org_name, current_date
            )
            
            # 워드클라우드 데이터가 없는 경우 기본 워드클라우드 반환
            if not wordcloud_data:
                logger.info(f"기관 '{org_name}'의 워드클라우드 데이터가 없어 기본 워드클라우드 반환")
                
                # 기본 워드클라우드 구성
                default_words = [WordItem(text="죄송합니다", value=100)]
                empty_wordcloud = EmptyWordCloud(
                    words=default_words,
                    period=None,
                    generated_at=None
                )
                
                # 기관 정보 (id=0, name=기관명)
                organization_info = OrganizationInfo(id=0, name=org_name)
                
                response_data = EmptyWordCloudData(
                    organization=organization_info,
                    wordcloud=empty_wordcloud
                )
                
                return EmptyWordCloudResponse(
                    success=True,
                    data=response_data
                )
            
            # 성공적인 워드클라우드 데이터 처리
            organization_info = OrganizationInfo(
                id=wordcloud_data["organization"]["id"],
                name=wordcloud_data["organization"]["name"]
            )
            
            # 연도별 워드클라우드 데이터 변환
            wordclouds_by_year = []
            for wordcloud_item in wordcloud_data["wordclouds"]:
                # JSON cloud_data를 WordItem 리스트로 변환
                word_items = []
                for word_data in wordcloud_item["cloud_data"]:
                    word_item = WordItem(
                        text=word_data["text"],
                        value=round(word_data["value"])  # float → int 반올림
                    )
                    word_items.append(word_item)
                
                # 기간 정보 구성
                period = WordCloudPeriod(
                    start_date=wordcloud_item["period_start"],
                    end_date=wordcloud_item["period_end"]
                )
                
                # 연도 추출 (period_start에서)
                year = wordcloud_item["period_start"].year
                
                # 연도별 워드클라우드 구성
                wordcloud_by_year = WordCloudByYear(
                    year=year,
                    words=word_items,
                    period=period,
                    generated_at=wordcloud_item["created_at"]
                )
                wordclouds_by_year.append(wordcloud_by_year)
            
            # 최종 응답 데이터 구성
            response_data = WordCloudData(
                organization=organization_info,
                wordclouds=wordclouds_by_year
            )
            
            logger.info(f"기관 '{org_name}'의 워드클라우드 {len(wordclouds_by_year)}개 연도 데이터 조회 완료")
            
            return WordCloudResponse(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            logger.error(f"기관 '{org_name}' 워드클라우드 조회 중 오류 발생: {str(e)}")
            raise Exception(f"기관 '{org_name}' 워드클라우드 조회에 실패했습니다: {str(e)}")