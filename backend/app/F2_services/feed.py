from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, Optional
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
    FeedFilter,
    LatestFeedData,
    LatestFeedItem,
    LatestFeedResponse,
    OrganizationLatestFeedData,
    OrganizationLatestFeedItem,
    OrganizationLatestFeedResponse,
    Top5FeedData,
    Top5FeedItem,
    Top5FeedResponse,
    PressReleaseData,
    PressReleaseItem,
    PressReleaseQuery,
    PressReleaseResponse,
    FeedDetail,
    FeedDetailData,
    FeedDetailResponse,
    RatingResponse, 
    RatingData,
    BookmarkResponse,
    BookmarkData,
    BookmarkRequest
)

from app.F6_schemas.base import PaginationInfo, ErrorResponse, ErrorDetail, ErrorCode, Message, Settings

logger = logging.getLogger(__name__)

class FeedService:
    def __init__(self, repo: FeedRepository):
        self.feed_repository = repo

    
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
                message=Message.SUCCESS,
                data=response_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_main_feed_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
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
                            code=ErrorCode.NOT_FOUND,
                            message=Message.NOT_FOUND
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
                message=Message.SUCCESS,
                data=response_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_organization_feed_list: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    # 메인 페이지용 최신 피드 슬라이드 조회 서비스
    # 입력: 
    #   limit - 최대 피드 수 제한 (int)
    # 반환: 
    #   LatestFeedResponse - 성공 시 최신 피드 데이터
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   각 기관별 최신 피드를 조회하여 메인 페이지 슬라이드용 데이터로 변환
    #   Repository에서 None 반환 시 적절한 에러 메시지 제공
    #   예외 발생 시 로깅 후 표준화된 에러 응답 반환
    async def get_latest_feeds_for_main(self, limit: int) -> LatestFeedResponse:
        try:
            # Repository를 통해 기관별 최신 피드 데이터 조회
            feeds_data = await self.feed_repository.get_latest_feeds_by_organization(limit)
            
            # Repository에서 None 반환 시 (데이터 없음) 에러 응답
            if feeds_data is None:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            # Repository 데이터를 스키마에 맞게 변환
            latest_feed_items = []
            for feed in feeds_data:
                # 기관 정보 객체 생성
                organization_info = OrganizationInfo(
                    id=feed['organization_id'],
                    name=feed['organization_name']
                )
                
                # 최신 피드 항목 객체 생성
                feed_item = LatestFeedItem(
                    id=feed['id'],
                    title=feed['title'],
                    organization=organization_info
                )
                latest_feed_items.append(feed_item)
            
            # 최신 피드 데이터 객체 생성
            latest_feed_data = LatestFeedData(
                feeds=latest_feed_items,
                count=len(latest_feed_items)
            )
            
            # 성공 응답 반환
            return LatestFeedResponse(
                success=True,
                message=Message.SUCCESS,
                data=latest_feed_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_latest_feeds_for_main: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    # 기관 페이지용 최신 피드 슬라이드 조회 서비스
    # 입력: 
    #   organization_name - 기관명 (str)
    #   limit - 최대 카테고리 수 제한 (int)
    # 반환: 
    #   OrganizationLatestFeedResponse - 성공 시 기관별 최신 피드 데이터
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   특정 기관의 카테고리별 최신 피드를 조회하여 기관 페이지 슬라이드용 데이터로 변환
    #   Repository에서 None 반환 시 적절한 에러 메시지 제공
    #   예외 발생 시 로깅 후 표준화된 에러 응답 반환
    async def get_organization_latest_feeds(self, organization_name: str, limit: int) -> OrganizationLatestFeedResponse:
        try:
            # Repository를 통해 기관별 카테고리별 최신 피드 데이터 조회
            feeds_data = await self.feed_repository.get_organization_latest_feeds_by_category(
                organization_name, limit
            )
            
            # Repository에서 None 반환 시 (데이터 없음) 에러 응답
            if feeds_data is None:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            # 기관 정보 객체 생성
            organization_info = OrganizationInfo(
                id=feeds_data['organization']['id'],
                name=feeds_data['organization']['name']
            )
            
            # Repository 피드 데이터를 스키마에 맞게 변환
            organization_latest_feed_items = []
            for feed in feeds_data['feeds']:
                # 카테고리 정보 객체 생성
                category_info = CategoryInfo(
                    id=feed['category_id'],
                    name=feed['category_name']
                )
                
                # 기관 최신 피드 항목 객체 생성
                feed_item = OrganizationLatestFeedItem(
                    id=feed['id'],
                    title=feed['title'],
                    category=category_info
                )
                organization_latest_feed_items.append(feed_item)
            
            # 기관 최신 피드 데이터 객체 생성
            organization_latest_feed_data = OrganizationLatestFeedData(
                organization=organization_info,
                feeds=organization_latest_feed_items,
                count=len(organization_latest_feed_items)
            )
            
            # 성공 응답 반환
            return OrganizationLatestFeedResponse(
                success=True,
                message=Message.SUCCESS,
                data=organization_latest_feed_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_organization_latest_feeds: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    # TOP5 피드 조회 서비스
    # 입력: 
    #   limit - 각 기준별 피드 수 제한 (int)
    # 반환: 
    #   Top5FeedResponse - 성공 시 TOP5 피드 데이터
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   조회수, 평균 별점, 북마크 수 기준으로 각각 상위 피드를 조회
    #   Repository에서 None 반환 시 빈 리스트로 처리
    #   예외 발생 시 로깅 후 표준화된 에러 응답 반환
    async def get_top5_feeds(self, limit: int) -> Top5FeedResponse:
        try:
            # Repository를 통해 3가지 기준별 상위 피드 데이터 조회
            top_viewed_data = await self.feed_repository.get_top5_viewed(limit)
            top_rated_data = await self.feed_repository.get_top5_rated(limit)
            top_bookmarked_data = await self.feed_repository.get_top5_bookmarked(limit)
            
            # None인 경우 빈 리스트로 처리
            top_viewed_data = top_viewed_data or []
            top_rated_data = top_rated_data or []
            top_bookmarked_data = top_bookmarked_data or []
            
            # 조회수 기준 피드 데이터를 스키마에 맞게 변환
            most_viewed_items = []
            for feed in top_viewed_data:
                feed_item = Top5FeedItem(
                    id=feed['id'],
                    title=feed['title'],
                    average_rating=feed['average_rating'] if feed['average_rating'] is not None else 0.0,
                    view_count=feed['view_count'],
                    bookmark_count=feed['bookmark_count']
                )
                most_viewed_items.append(feed_item)
            
            # 평균 별점 기준 피드 데이터를 스키마에 맞게 변환
            top_rated_items = []
            for feed in top_rated_data:
                feed_item = Top5FeedItem(
                    id=feed['id'],
                    title=feed['title'],
                    average_rating=feed['average_rating'],  # 별점 기준이므로 항상 값 존재
                    view_count=feed['view_count'],
                    bookmark_count=feed['bookmark_count']
                )
                top_rated_items.append(feed_item)
            
            # 북마크 수 기준 피드 데이터를 스키마에 맞게 변환
            most_bookmarked_items = []
            for feed in top_bookmarked_data:
                feed_item = Top5FeedItem(
                    id=feed['id'],
                    title=feed['title'],
                    average_rating=feed['average_rating'] if feed['average_rating'] is not None else 0.0,
                    view_count=feed['view_count'],
                    bookmark_count=feed['bookmark_count']
                )
                most_bookmarked_items.append(feed_item)
            
            # TOP5 피드 데이터 객체 생성
            top5_feed_data = Top5FeedData(
                top_rated=top_rated_items,
                most_viewed=most_viewed_items,
                most_bookmarked=most_bookmarked_items
            )
            
            # 성공 응답 반환
            return Top5FeedResponse(
                success=True,
                message=Message.SUCCESS,
                data=top5_feed_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_top5_feeds: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
    
    # 기관별 보도자료 목록 조회 서비스
    # 입력: 
    #   organization_name - 기관명 (str)
    #   query - 페이지네이션 쿼리 파라미터 (PressReleaseQuery)
    # 반환: 
    #   PressReleaseResponse - 성공 시 보도자료 데이터
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   특정 기관의 보도자료 목록을 페이지네이션과 함께 조회
    #   Repository에서 None 반환 시 적절한 에러 메시지 제공
    #   더보기 방식을 고려한 페이지네이션 정보 생성
    #   예외 발생 시 로깅 후 표준화된 에러 응답 반환
    async def get_organization_press_releases(self, organization_name: str, query: PressReleaseQuery) -> PressReleaseResponse:
        try:
            # offset 계산 (페이지네이션용)
            offset = (query.page - 1) * query.limit
            
            # Repository를 통해 기관별 보도자료 데이터 조회
            press_data = await self.feed_repository.get_organization_press(
                organization_name, offset, query.limit
            )
            
            # Repository에서 None 반환 시 (데이터 없음) 에러 응답
            if press_data is None:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )
            
            # 기관 정보 객체 생성
            organization_info = OrganizationInfo(
                id=press_data['organization']['id'],
                name=press_data['organization']['name']
            )
            
            # Repository 보도자료 데이터를 스키마에 맞게 변환
            press_release_items = []
            for press_release in press_data['press_releases']:
                # 카테고리 정보 객체 생성
                category_info = CategoryInfo(
                    id=press_release['category_id'],
                    name=press_release['category_name']
                )
                
                # 보도자료 항목 객체 생성
                press_item = PressReleaseItem(
                    id=press_release['id'],
                    title=press_release['title'],
                    category=category_info,
                    summary=press_release['summary'],
                    published_date=press_release['published_date'],
                    view_count=press_release['view_count'],
                    average_rating=press_release['average_rating']  # Repository에서 0.0 처리됨
                )
                press_release_items.append(press_item)
            
            # 페이지네이션 정보 생성 (더보기 방식 고려)
            pagination_info = PaginationInfo(
                current_page=query.page,
                total_pages=0,  # 더보기 방식이므로 의미 없음
                total_count=0,  # 더보기 방식이므로 의미 없음
                limit=query.limit,
                has_next=press_data['has_more'],  # Repository의 has_more 사용
                has_previous=query.page > 1
            )
            
            # 보도자료 데이터 객체 생성
            press_release_data = PressReleaseData(
                organization=organization_info,
                press_releases=press_release_items,
                pagination=pagination_info
            )
            
            # 성공 응답 반환
            return PressReleaseResponse(
                success=True,
                message=Message.SUCCESS,
                data=press_release_data
            )
            
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_organization_press_releases: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    # 피드 상세 페이지용 피드 정보 조회 서비스
    # 입력: 
    #   feed_id - 조회할 피드 ID (int)
    # 반환: 
    #   FeedDetailResponse - 성공 시 피드 상세 데이터
    #   ErrorResponse - 실패 시 에러 정보
    # 설명: 
    #   특정 피드의 상세 정보를 조회하여 피드 상세 페이지용 데이터로 변환
    #   PDF 통째로 전달해버림
    #   조회 성공 시 해당 피드의 조회수를 1 증가시킴
    #   Repository에서 None 반환 시 적절한 에러 메시지 제공
    #   예외 발생 시 로깅 후 표준화된 에러 응답 반환
    async def get_feed_detail_for_page(
        self, feed_id: int, user_id: Optional[int] = None
    ) -> Union[FeedDetailResponse, ErrorResponse]:
        try:
            feed_data = await self.feed_repository.get_feed_detail(feed_id)
            
            if feed_data is None:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.NOT_FOUND
                    )
                )

            # 조회수 증가
            await self.feed_repository.increment_feed_view_count(feed_id)
            
            
            # 1. pdf_url 생성
            pdf_url = f"{Settings.STATIC_FILES_URL}/feeds_pdf/{feed_data['pdf_file_path']}"
            # pdf_url = f"{feed_data['pdf_file_path']}"

            # 2. 사용자별 정보 초기화
            is_bookmarked = None
            user_rating = None

            # 3. 로그인한 사용자(user_id가 주어짐)인 경우, 추가 정보 조회
            if user_id:
                # 북마크 여부 확인
                bookmark = await self.feed_repository.get_bookmark(user_id, feed_id)
                is_bookmarked = bookmark is not None
                
                # 사용자가 매긴 별점 확인
                rating = await self.feed_repository.get_user_rating_for_feed(user_id, feed_id)
                user_rating = rating.score if rating else None
            
            organization_info = OrganizationInfo(id=feed_data['organization_id'], name=feed_data['organization_name'])
            category_info = CategoryInfo(id=feed_data['category_id'], name=feed_data['category_name'])
            
            feed_detail = FeedDetail(
                id=feed_data['id'],
                title=feed_data['title'],
                organization=organization_info,
                category=category_info,
                average_rating=feed_data['average_rating'],
                view_count=feed_data['view_count'] + 1, # 조회수 증가를 즉시 반영
                published_date=feed_data['published_date'],
                source_url=feed_data['source_url'],
                # 수정된 스키마에 맞춰 데이터 전달
                pdf_url=pdf_url,
                is_bookmarked=is_bookmarked, 
                user_rating=user_rating
            )
            
            feed_detail_data = FeedDetailData(feed=feed_detail)
            
            return FeedDetailResponse(success=True, data=feed_detail_data)
            
        except Exception as e:
            logger.error(f"Error in get_feed_detail_for_page: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        

    async def post_feed_rating(self, feed_id: int, user_id: str, score: int)-> RatingResponse:
        try:
            # user_id를 통해 user pk 구하기
            user_pk = await self.feed_repository.get_user_pk_by_user_id(user_id)
            
            if not user_pk:
                logger.warning(f"존재하지 않는 사용자 - user_id: {user_id}")
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
                    )
                )
            
            # 피드 존재 여부
            is_exists = await self.feed_repository.is_feed_exists(feed_id)

            if not is_exists: 
                logger.warning(f"존재하지 않는 피드 - feed_id: {feed_id}")
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.FEED_NOT_FOUND
                    )
                )
        
            # 이미 평점 존재하는 경우
            already_rated = await self.feed_repository.is_rating_exists(feed_id, user_pk)
            
            if already_rated:
                logger.warning(f"이미 완료된 피드 - feed_id: {feed_id}")
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.ALREADY_EXISTS,
                        message=Message.RATING_ALEADY_EXIST
                    )
                )
            

            # 점수 유효성 (중복 검사)
            if not (1 <= score <= 5):
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INVALID_PARAMETER,
                        message=Message.INVALID_RATING_SCORE
                    )
                )

            # 평점 등록
            await self.feed_repository.register_rating(feed_id, user_pk, score)

            # 평점 통계 조회
            rating_stats  = await self.feed_repository.get_feed_rating(feed_id)
            # 반환
            return RatingResponse(
                success=True,
                data = RatingData(
                    user_rating=score,
                    average_rating= rating_stats["average_rating"],
                    total_ratings= rating_stats["total_ratings"],
                    message= Message.SUCCESS
                )
            )

        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in post_feed_rating_for_page: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
    
    async def post_feed_bookmark(self, feed_id: int, user_id: str) -> BookmarkResponse | ErrorResponse:
        # user_id로 user_pk 조회
        user_pk = await self.feed_repository.get_user_pk_by_user_id(user_id)

        if not user_pk:
            logger.warning(f"존재하지 않는 사용자 - user_id: {user_id}")
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.NOT_FOUND,
                    message=Message.USER_NOT_FOUND
                )
            )
        
        # feed 존재 여부 확인
        is_exists = await self.feed_repository.is_feed_exists(feed_id)

        if not is_exists: 
            logger.warning(f"존재하지 않는 피드 - feed_id: {feed_id}")
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.NOT_FOUND,
                    message=Message.FEED_NOT_FOUND
                )
            )
        
        # 북마크 존재 여부 확인
        bookmark = await self.feed_repository.get_bookmark(user_pk, feed_id)

        if bookmark:
            # 북마크 존재하면 제거
            await self.feed_repository.delete_bookmark(bookmark.id)
            # 북마크 개수 조회
            bookmark_count = await self.feed_repository.get_bookmark_count(feed_id)
            return BookmarkResponse(
                success=True,
                data = BookmarkData(
                    is_bookmarked=False,
                    bookmark_count=bookmark_count,
                    message=Message.DELETED
                )
            )
        else:
            # 북마크 없으면 추가
            await self.feed_repository.create_bookmark(user_pk, feed_id)
            # 북마크 개수 조회
            bookmark_count = await self.feed_repository.get_bookmark_count(feed_id)
            return BookmarkResponse(
                success=True,
                data = BookmarkData(
                    is_bookmarked=True,
                    bookmark_count=bookmark_count,
                    message=Message.SUCCESS
                )
            )
