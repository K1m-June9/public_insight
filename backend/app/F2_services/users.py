from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import math
import logging
from fastapi import HTTPException, status, Depends, BackgroundTasks

from app.F3_repositories.users import UserRepository
from app.F4_utils.validators import validate_nickname, validate_password
from app.F5_core.security import auth_handler
from app.F6_schemas.base import (
    PaginationInfo, ErrorResponse, ErrorDetail
)
from app.F6_schemas.users import (
    UserRatingListQuery, UserRatingListResponse, RatingItem, UserRatingListData, 
    UserBookmarkListQuery, UserBookmarkListResponse, UserBookmarkListData
)

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository):
        # UserRepository 인스턴스를 주입받아 DB 접근에 사용
        self.repo = repo

    async def update_nickname(self, user_id: str, nickname: str) -> Optional[str]:
        """nickname 변경"""
        
        # 1. 유효성 검사
        if not validate_nickname(nickname):
            logger.info(f"Nickname validation failed: {nickname}")
            return None 

        # 2. 중복 검사 (본인 제외)
        exists = await self.repo.is_nickname_exists(nickname, exclude_user_id=user_id)
        if exists:
            logger.info(f"Nickname exists check: {nickname} => {exists}")
            return None
        
        # 3. 닉네임 업데이트
        await self.repo.update_nickname(user_id, nickname)
        return nickname
    

    async def update_password(self, user_id: str, current_password: str, new_password: str):
        """비밀번호 변경"""
        user = await self.repo.get_user_by_user_id(user_id)
        
        # 1. 현재 비밀번호 검사
        if not auth_handler.verify_password(current_password, user.password_hash):
            logger.warning(f"[{user_id}] 현재 비밀번호가 일치하지 않음")
            return False
        

        # 2. current_password와 new_password가 동일하면 안됨
        if auth_handler.verify_password(new_password, user.password_hash):
            logger.warning(f"[{user_id}] 새 비밀번호가 기존 비밀번호와 동일함")
            return False


        # 3. 새로운 비밀번호 유효성 검사
        if not validate_password(new_password):
            logger.info(f"[{user_id}] 새 비밀번호 유효성 검사 실패")
            return False
        

        # 4. 비밀번호 해시 및 업데이트
        new_hash = auth_handler.get_password_hash(new_password)
        await self.repo.update_password(user_id, new_hash)
        
        logger.info(f"[{user_id}] 비밀번호 변경 완료")
        return True
    


    async def get_my_ratings(
            self, query: UserRatingListQuery, user_id: str
    ) -> UserRatingListResponse | ErrorResponse:
        """특정 사용자가 남긴 별점 목록과 페이지네이션 정보를 반환"""
        try: 
            # 1. 유저 PK 조회
            # user_id로 부터 내부 DB에 저장된 실제 user_pk(id)를 가져옴
            user_pk = await self.repo.get_user_pk_by_user_id(user_id)
            if user_pk is None:
                # 유저가 없으면 에러 응답 반환
                return ErrorResponse(
                    error=ErrorDetail(
                        code="USER_NOT_FOUND",
                        message="사용자를 찾을 수 없습니다"
                    )
                )

            # 2. 페이지 및 limit 값 가져오기
            # query 객체의 page와 limit 값을 추출
            # page/limit가 함수라면 호출해서 값 얻고, 아니라면 그대로 사용
            page = query.page() if callable(query.page) else query.page
            limit = query.limit() if callable(query.limit) else query.limit


            # 2-1. 유저가 남긴 총 별점 개수 조회
            total_count = await self.repo.get_total_ratings_count(user_pk)

            # 2-2. 총 페이지 수 계산(ceil 사용해 올림 처리)
            # total_count가 0인 경우 페이지 수를 최소 1로 설정
            total_pages = math.ceil(total_count / limit) if total_count > 0 else 1
            
            # math.ceil(total_count / query.limit) if total_count > 0 else 1
            # math.ceil(total_count / query.limit) if total_count > 0 else 0
            # max(math.ceil(total_count / query.limit), 1)

            # 3. 요청한 페이지가 범위를 벗어나면 빈 리스트 반환
            if page > total_pages and total_count > 0:
                ratings_list: list[RatingItem] = [] # 요청 범위를 벗어나면 빈 배열 반환
            else:
                # 3-1. 페이지네이션 offset 계산
                # 예: page=2, limit 10 이면
                # offset=(2-1)*10 = 10
                offset = (query.page - 1) * query.limit
                
                # 3-2. 유저의 별점 데이터 조회
                ratings_list = await self.repo.get_ratings_data(user_pk, offset, query.limit)
            
            # 4. 페이지네이션 정보 생성
            pagination_info = PaginationInfo(
                current_page=query.page,
                total_pages=total_pages,
                total_count=total_count,
                limit=query.limit,
                has_next=query.page < total_pages,
                has_previous=query.page > 1
            )

            # 5. 최종 응답 객체 구성
            response_data = UserRatingListResponse(
                success=True,
                data=UserRatingListData(
                    ratings=ratings_list,
                    pagination=pagination_info
                )
            )
            return response_data

        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_my_ratings: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다."
                )
            )
        
    
    async def get_my_bookmarks(self, query: UserBookmarkListQuery, user_id: str
    ) -> UserBookmarkListResponse | ErrorResponse:
        try:
            # 1. 유저 PK 조회
            # user_id로 부터 내부 DB에 저장된 실제 user_pk(id)를 가져옴
            user_pk = await self.repo.get_user_pk_by_user_id(user_id)
            if user_pk is None:
                # 유저가 없으면 에러 응답 반환
                return ErrorResponse(
                    error=ErrorDetail(
                        code="USER_NOT_FOUND",
                        message="사용자를 찾을 수 없습니다"
                    )
                )


            # 2. 페이지 및 limit 값 가져오기
            # query 객체의 page와 limit 값을 추출
            # page/limit가 함수라면 호출해서 값 얻고, 아니라면 그대로 사용
            page = query.page() if callable(query.page) else query.page
            limit = query.limit() if callable(query.limit) else query.limit

            # 2-1. 유저가 남긴 총 북마크 개수 조회
            total_count = await self.repo.get_total_bookmarks_count(user_pk)

            # 2-2. 총 페이지 수 계산(ceil 사용해 올림 처리)
            # total_count가 0인 경우 페이지 수를 최소 1로 설정
            total_pages = math.ceil(total_count / limit) if total_count > 0 else 1


            # 3. 요청한 페이지가 범위를 벗어나면 빈 리스트 반환
            if page > total_pages and total_count > 0:
                bookmarks_list: list[RatingItem] = [] # 요청 범위를 벗어나면 빈 배열 반환
            else:
                # 3-1. 페이지네이션 offset 계산
                # 예: page=2, limit 10 이면
                # offset=(2-1)*10 = 10
                offset = (query.page - 1) * query.limit
                
                # 3-2. 유저의 별점 데이터 조회
                bookmarks_list = await self.repo.get_bookmarks_data(user_pk, offset, query.limit)
            

            # 4. 페이지네이션 정보 생성
            pagination_info = PaginationInfo(
                current_page=query.page,
                total_pages=total_pages,
                total_count=total_count,
                limit=query.limit,
                has_next=query.page < total_pages,
                has_previous=query.page > 1
            )

            # 5. 최종 응답 객체 구성
            response_data = UserBookmarkListResponse(
                success=True,
                data=UserBookmarkListData(
                    bookmarks=bookmarks_list,
                    pagination=pagination_info
                )
            )
            return response_data

        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in get_my_bookmarks: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다."
                )
            )