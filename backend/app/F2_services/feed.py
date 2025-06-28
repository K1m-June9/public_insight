from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging
import math
from app.F3_repositories.feed import FeedRepository
from app.F6_schemas.feed import (
    FeedListQuery, 
    MainFeedListResponse, 
    MainFeedListData, 
    MainFeedItem, 
    OrganizationInfo,
    OrganizationFeedItem,
    OrganizationFeedListData,
    OrganizationFeedListResponse,
    OrganizationFeedQuery,
    CategoryInfo,
    FeedFilter
)
from app.F6_schemas.base import PaginationInfo, ErrorResponse, ErrorDetail

logger = logging.getLogger(__name__)

class FeedService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.feed_repository = FeedRepository(db)
    
    # 메인 페이지 피드 목록 조회 서비스 메서드
    # 입력: 
    #   query - 페이지네이션 쿼리 파라미터 (FeedListQuery)
    # 반환: 
    #   메인 페이지 피드 목록 응답 (MainFeedListResponse) 또는 에러 응답 (ErrorResponse)
    # 설명: 
    #   Repository에서 조회한 피드 데이터를 스키마에 맞게 변환하고 페이지네이션 처리
    #   - 기관 정보를 OrganizationInfo 객체로 통합
    #   - 평균 별점이 None인 경우 0.0으로 변환
    #   - 페이지네이션 정보 계산 (total_pages, has_next, has_previous 등)
    #   - 빈 결과나 페이지 범위 초과 시 공백 리스트 반환
    #   - 예외 발생 시 표준화된 에러 응답 반환
    async def get_main_feed_list(self, query: FeedListQuery) -> MainFeedListResponse:
        try:
            # Repository에서 전체 피드 데이터 조회
            feeds_data = await self.feed_repository.get_feeds_with_details()
            
            # 전체 데이터 개수 계산
            total_count = len(feeds_data)
            
            # 전체 페이지 수 계산 (올림 처리)
            total_pages = math.ceil(total_count / query.limit) if total_count > 0 else 0
            
            # 현재 페이지가 범위를 벗어나는 경우 공백 리스트 반환
            if query.page > total_pages and total_count > 0:
                feeds_list = []
            else:
                # 페이지별 데이터 슬라이싱 계산
                start_index = (query.page - 1) * query.limit
                end_index = start_index + query.limit
                
                # 해당 페이지의 데이터만 추출
                page_feeds_data = feeds_data[start_index:end_index]
                
                # Repository 데이터를 스키마 형태로 변환
                feeds_list = []
                for feed_data in page_feeds_data:
                    # 기관 정보를 OrganizationInfo 객체로 변환
                    organization_info = OrganizationInfo(
                        id=feed_data['organization_id'],
                        name=feed_data['organization_name']
                    )
                    
                    # 평균 별점이 None인 경우 0.0으로 변환
                    average_rating = feed_data['average_rating'] if feed_data['average_rating'] is not None else 0.0
                    
                    # MainFeedItem 객체 생성
                    feed_item = MainFeedItem(
                        id=feed_data['id'],
                        title=feed_data['title'],
                        organization=organization_info,
                        summary=feed_data['summary'],
                        published_date=feed_data['published_date'],
                        view_count=feed_data['view_count'],
                        average_rating=average_rating
                    )
                    feeds_list.append(feed_item)
            
            # 페이지네이션 정보 계산
            pagination_info = PaginationInfo(
                current_page=query.page,
                total_pages=total_pages,
                total_count=total_count,
                limit=query.limit,
                has_next=query.page < total_pages,
                has_previous=query.page > 1
            )
            
            # 응답 데이터 구성
            response_data = MainFeedListData(
                feeds=feeds_list,
                pagination=pagination_info
            )
            
            # 최종 응답 반환
            return MainFeedListResponse(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_main_feed_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다."
                )
            )
    
    # 기관별 피드 목록 조회 서비스 메서드
    # 입력: 
    #   organization_name - 조회할 기관명 (str)
    #   query - 페이지네이션 및 카테고리 필터 쿼리 파라미터 (OrganizationFeedQuery)
    # 반환: 
    #   기관 페이지 피드 목록 응답 (OrganizationFeedListResponse) 또는 에러 응답 (ErrorResponse)
    # 설명: 
    #   Repository에서 조회한 특정 기관의 피드 데이터를 스키마에 맞게 변환하고 페이지네이션 처리
    #   - 기관 정보와 카테고리 정보를 각각 객체로 변환
    #   - 평균 별점이 None인 경우 0.0으로 변환
    #   - 페이지네이션 정보 계산 (total_pages, has_next, has_previous 등)
    #   - category_id 제공 시 필터 정보 포함
    #   - 존재하지 않는 기관명일 경우 에러 응답 반환
    #   - 예외 발생 시 표준화된 에러 응답 반환
    async def get_organization_feed_list(self, organization_name: str, query: OrganizationFeedQuery) -> OrganizationFeedListResponse:
        try:
            # Repository에서 기관별 피드 데이터 조회
            feeds_data = await self.feed_repository.get_feeds_by_organization_name(
                organization_name=organization_name,
                category_id=query.category_id
            )
            
            # 존재하지 않는 기관명인 경우 에러 응답 반환
            if not feeds_data:
                # 기관 자체가 존재하지 않는지 확인하기 위해 category_id 없이 재조회
                check_data = await self.feed_repository.get_feeds_by_organization_name(
                    organization_name=organization_name,
                    category_id=None
                )
                if not check_data:
                    return ErrorResponse(
                        error=ErrorDetail(
                            code="ORGANIZATION_NOT_FOUND",
                            message="존재하지 않는 기관입니다."
                        )
                    )
            
            # 전체 데이터 개수 계산
            total_count = len(feeds_data)
            
            # 전체 페이지 수 계산 (올림 처리)
            total_pages = math.ceil(total_count / query.limit) if total_count > 0 else 0
            
            # 현재 페이지가 범위를 벗어나는 경우 공백 리스트 반환
            if query.page > total_pages and total_count > 0:
                feeds_list = []
                page_feeds_data = []
            else:
                # 페이지별 데이터 슬라이싱 계산
                start_index = (query.page - 1) * query.limit
                end_index = start_index + query.limit
                
                # 해당 페이지의 데이터만 추출
                page_feeds_data = feeds_data[start_index:end_index]
                
                # Repository 데이터를 스키마 형태로 변환
                feeds_list = []
                for feed_data in page_feeds_data:
                    # 카테고리 정보를 CategoryInfo 객체로 변환
                    category_info = CategoryInfo(
                        id=feed_data['category_id'],
                        name=feed_data['category_name']
                    )
                    
                    # 평균 별점이 None인 경우 0.0으로 변환
                    average_rating = feed_data['average_rating'] if feed_data['average_rating'] is not None else 0.0
                    
                    # OrganizationFeedItem 객체 생성
                    feed_item = OrganizationFeedItem(
                        id=feed_data['id'],
                        title=feed_data['title'],
                        category=category_info,
                        summary=feed_data['summary'],
                        published_date=feed_data['published_date'],
                        view_count=feed_data['view_count'],
                        average_rating=average_rating
                    )
                    feeds_list.append(feed_item)
            
            # 기관 정보 생성 (빈 결과여도 항상 표시)
            organization_info = None
            if feeds_data:
                # 데이터가 있는 경우 첫 번째 항목에서 기관 정보 추출
                first_feed = feeds_data[0]
                organization_info = OrganizationInfo(
                    id=first_feed['organization_id'],
                    name=first_feed['organization_name']
                )
            else:
                # 빈 결과인 경우 기관명으로 기관 정보 생성 (ID는 임시로 0 설정)
                # 실제로는 기관 정보를 별도로 조회해야 하지만, 현재는 간단히 처리
                organization_info = OrganizationInfo(
                    id=0,  # 임시 ID
                    name=organization_name
                )
            
            # 페이지네이션 정보 계산
            pagination_info = PaginationInfo(
                current_page=query.page,
                total_pages=total_pages,
                total_count=total_count,
                limit=query.limit,
                has_next=query.page < total_pages,
                has_previous=query.page > 1
            )
            
            # 필터 정보 생성 (category_id가 제공된 경우)
            filter_info = None
            if query.category_id is not None and page_feeds_data:
                # 실제 데이터에서 카테고리 정보 추출
                first_feed = page_feeds_data[0]
                filter_info = FeedFilter(
                    category_id=first_feed['category_id'],
                    category_name=first_feed['category_name']
                )
            
            # 응답 데이터 구성
            response_data = OrganizationFeedListData(
                organization=organization_info,
                feeds=feeds_list,
                pagination=pagination_info,
                filter=filter_info
            )
            
            # 최종 응답 반환
            return OrganizationFeedListResponse(
                success=True,
                data=response_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_organization_feed_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다."
                )
            )