import logging
import math 
from datetime import datetime

from app.F3_repositories.notice import NoticeRepository
from app.F6_schemas.base import ErrorResponse, ErrorDetail, PaginationInfo
from app.F6_schemas.notice import  (
    NoticeListQuery, NoticeListResponse, NoticeListItem, NoticeListData,
    NoticeDetailResponse, NoticeDetail, NoticeDetailData, PinnedNoticeResponse,
    PinnedNoticeItem, PinnedNoticeData, PinnedNoticeResponse
)


logger = logging.getLogger(__name__)


class NoticeService:
    def __init__(self, repo: NoticeRepository):
        # NoticeRepository 인스턴스를 주입받아 DB 접근에 사용
        self.repo = repo

    async def get_pinned_notice(self) -> PinnedNoticeResponse:
        """고정된 공지사항을 조회"""
        try:   
            # 1. 고정된 공지사항 데이터 조회 (dict 형태 리스트 반환)
            pinned_notices_data = await self.repo.fetch_pinned_notice()
            
            # 2. 조회된 공지사항 개수 계산
            total_count = len(pinned_notices_data)
            
            # 3. 각 공지사항 dict를 PinnedNoticeItem 객체로 변환
            pinned_notices_list = [
                PinnedNoticeItem(**item) for item in pinned_notices_data
            ]
            
            # 4. PinnedNoticeData 스키마에 변환된 리스트와 카운트 담기
            response_data = PinnedNoticeData(
                notices=pinned_notices_list, 
                count=total_count
            )
            
            # 5. 최종 응답
            return PinnedNoticeResponse(success=True, data=response_data)

        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_main_feed_list: {e}", exc_info=True)

            # 서버 내부 오류 에러 응답 반환
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다"
                )
            )

    async def get_main_notice_list(self, query:  NoticeListQuery) -> NoticeListResponse:
        try: 
            # Repository에서 전체 피드 데이터 조회
            notices_data = await self.repo.get_notices_with_details()

            # 전체 데이터 개수 계산
            total_count = len(notices_data)

            # 전체 페이지 수 계산 (올림 처리)
            total_pages = math.ceil(total_count / query.limit) if total_count > 0 else 0

            # 현재 페이지가 범위를 벗어나는 경우 공백 리스트 반환
            if query.page > total_pages and total_count > 0:
                notices_list = []
            else:
                # 페이지별 데이터 슬라이싱 계산
                start_index = (query.page - 1) * query.limit
                end_index = start_index + query.limit
                
                # 해당 페이지의 데이터만 추출
                page_notices_data = notices_data[start_index:end_index]
                
                # Repository 데이터를 스키마 형태로 변환
                notices_list = []
                for notice_data in page_notices_data:

                    notice_item = NoticeListItem(
                        id=notice_data['id'],
                        title=notice_data['title'],
                        author=notice_data['author'],
                        is_pinned=notice_data['is_pinned'],
                        created_at=notice_data['created_at']
                    )
                    notices_list.append(notice_item)
            
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
            response_data = NoticeListData(
                notices=notices_list,
                pagination=pagination_info
            )
            
            # 최종 응답 반환
            return NoticeListResponse(
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



    async def get_notice_detail(self, notice_id: int) -> NoticeDetailResponse:
        """
        공지사항 ID로 상세 정보를 조회
        - 유효하지 않은 ID는 에러 반환
        - 공지사항이 존재하지 않거나 비활성화된 경우 에러 반환
        - 조회수는 자동 증가
        """
        try:
            # 1. ID 유효성 검증
            if notice_id <= 0:
                return ErrorResponse(
                    error=ErrorDetail(
                        code="INVALID_NOTICE_ID",
                        message="올바르지 않은 공지사항 ID입니다"
                    )
                )
            
            # 2. 공지사항 조회
            notice = await self.repo.get_notice_by_id(notice_id)
            if not notice:
                return ErrorResponse(
                    error=ErrorDetail(
                        code="NOTICE_NOT_FOUND",
                        message="공지사항을 찾을 수 없습니다"
                    )
                )

            notice_id = notice.id
            title = notice.title
            author = notice.author
            content = notice.content
            is_pinned = notice.is_pinned
            view_count = notice.view_count
            created_at = notice.created_at
            updated_at = notice.updated_at

            # 3. 조회수 증가 (실패하더라고 계속 진행)
            view_count_result = await self.repo.increment_notice_view_count(notice_id)
            if not view_count_result:
                logger.warning(f"공지사항 조회수 증가 실패 - notice_id: {notice_id}")

            
            # 4. NoticeDetail 스키마로 변환
            notice_detail = NoticeDetail(
                id=notice_id,
                title=title,
                author=author,
                content=content,
                is_pinned=is_pinned,
                view_count=view_count + 1 if view_count_result else view_count,
                created_at=created_at,
                updated_at=updated_at
            )
            
            # 5. 최종 응답
            return NoticeDetailResponse(
                success=True, 
                data=NoticeDetailData(notice=notice_detail))
            
        except Exception as e:
            logger.error(f"공지사항 상세 조회 중 오류 발생 - notice_id: {notice_id}, error: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="공지사항을 조회하는 중 오류가 발생했습니다"
                )
            )
