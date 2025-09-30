import math
import logging
from typing import Union, List, Set, Dict, Optional

from app.F2_services.session import SessionService
from app.F3_repositories.users import UserRepository
from app.F4_utils.validators import validate_nickname, validate_password
from app.F5_core.security import auth_handler
from app.F5_core.redis import RedisCacheService
from app.F14_knowledge_graph.graph_ml import predict_similar_nodes
from datetime import datetime
from neo4j.time import DateTime as Neo4jDateTime

from app.F6_schemas.base import (
    ErrorCode,
    Message,
    PaginationInfo, 
    ErrorResponse, 
    ErrorDetail,
    UserRole
)

from app.F6_schemas.users import (
    UserProfileResponse,
    UserProfile,
    UserProfileData,
    UserPasswordUpdateResponse,
    UserRatingListQuery, 
    UserRatingListResponse, 
    RatingItem, 
    UserRatingListData, 
    UserBookmarkListQuery, 
    UserBookmarkListResponse, 
    UserBookmarkListData,
    UserRecommendationResponse, 
    UserRecommendationData, 
    RecommendedFeedItem, 
    RecommendedKeywordItem
)

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, repo: UserRepository, session_service: SessionService):
        # UserRepository 인스턴스를 주입받아 DB 접근에 사용
        self.repo = repo
        self.session_service = session_service


    async def update_nickname(self, user_id: str, email: str, nickname: str, role: UserRole) -> Union[UserProfileResponse, ErrorResponse]:
        """
        nickname 변경
        - /me/nickname
        """
        logger.debug(f"Service logic started. user_id='{user_id}', new_nickname='{nickname}'")
        try:
            # 1. 유효성 검사
            is_invalid = not validate_nickname(nickname)
            
            if is_invalid:

                log_message = "Nickname validation failed"
                log_extra = {
                    "event":{"action":"update_nickname", "outcome":"failure"},
                    "user":{"id":user_id},
                    "error":{"attempted_nickname":nickname}
                }
                logger.warning(log_message, extra=log_extra)

                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.VALIDATION_ERROR,
                        message=Message.VALIDATION_ERROR
                    )
                )
            
            # 2. 중복 검사(본인 제외)
            logger.debug(f"Checking for nickname duplication, excluding self. nickname='{nickname}'")
            is_duplicate = await self.repo.is_nickname_exists(nickname, exclude_user_id=user_id)

            if is_duplicate:

                log_message = "Duplicate nickname attempt"
                log_extra = {
                    "event": {"action": "update_nickname", "outcome": "failure"},
                    "user": {"id": user_id},
                    "error": {"type": "Duplicate Value", "reason": "Nickname already exists"},
                    "data": {"attempted_nickname": nickname}
                }
                logging.warning(log_message, extra=log_extra)
                return ErrorResponse(
                    error = ErrorDetail(
                        code=ErrorCode.DUPLICATE,
                        message=Message.DUPLICATE_NICKNAME
                )
            )
        
            # 3. 닉네임 업데이트
            logger.debug(f"Validation and duplication checks passed. Proceeding to update DB for user_id='{user_id}'.")
            await self.repo.update_nickname(user_id, nickname)

            # 4. 응답 데이터 구성
            response_data = UserProfileData(
                user=UserProfile(
                    user_id=user_id,
                    nickname=nickname,
                    email=email,
                    role=role
                )
            )

            # 5. 최종 응답 반환
            return UserProfileResponse(
                success=True,    
                data=response_data
            )
        
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(
                f"An unexpected database or logic error occurred in update_nickname service for user_id='{user_id}'.", 
                exc_info=True,
                extra={
                    # 에러 로그에도 일관된 ECS 구조를 추가하면 분석에 매우 유리합니다.
                    "event": {"action": "update_nickname", "outcome": "failure"},
                    "user": {"id": user_id},
                    "error": {"type": e.__class__.__name__, "message": str(e)}
                }
            )
            
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )



    async def update_password(
        self, 
        user_id: str, 
        current_password:str, 
        new_password: str,
        current_jti: str, 
        current_refresh_token: str
        )-> UserPasswordUpdateResponse: 
        """
        password 변경 후 후속 조치 처리
        1. 사용자 조회 및 현재 비밀번호 검증
        2. 새 비밀번호 유효성 및 기존 비밀번호와 중복 검사
        3. 비밀번호 업데이트
        4. 관련 캐시 무효화
        5. 현재 세션을 제외한 모든 세션 로그아웃

        """
        try:
            user = await self.repo.get_user_by_user_id(user_id)
            if not user:
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
                    )
                )
            
            # 1. 현재 비밀번호 검사
            if not auth_handler.verify_password(current_password, user.password_hash):
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.INVALID_PARAMETER, 
                        message=Message.INVALID_CREDENTIALS
                    )
                )


            # 2. 새 비밀번호 유효성 및 기존 비밀번호와 중복 검사
            if auth_handler.verify_password(new_password, user.password_hash):
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.DUPLICATE,
                        message=Message.DUPLICATE_PASSWROD
                    )
                )

            # 3. 새로운 비밀번호 유효성 검사
            if not validate_password(new_password):
                return ErrorResponse(
                    error=ErrorDetail(
                        code=ErrorCode.VALIDATION_ERROR,
                        message=Message.VALIDATION_PASSWORD
                    )
                )
            
            # 4. 비밀번호 해시 및 업데이트
            new_password_hash = auth_handler.get_password_hash(new_password)
            await self.repo.update_password(user_id, new_password_hash)
            
            # ---- 후처리 ----
            # 5. 사용자 정보 캐시 무효화
            await RedisCacheService.invalidate_user_cache(user_id)

            # 6. 현재 세션을 제외한 다른 모든 세션 로그아웃 처리
            await self.session_service.logout_other_sessions(
                user_id=user_id, 
                current_jti=current_jti, 
                current_refresh_token=current_refresh_token)
            
            # 7. 성공 응답 반환
            return UserPasswordUpdateResponse(
            success=True,
            message=Message.SUCCESS
            )
        
        except Exception as e:
            # 예외 발생 시 로깅 및 표준화된 에러 응답 반환
            logger.error(f"Error in update_password: {e}", exc_info=True)
            return ErrorResponse(
                error=ErrorDetail(
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )



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
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
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


            # 3. 요청한 페이지가 범위를 벗어나면 빈 리스트 반환
            if page > total_pages and total_count > 0:
                ratings_list: list[RatingItem] = [] # 요청 범위를 벗어나면 빈 배열 반환
            else:
                # 3-1. 페이지네이션 offset 계산
                # 예: page=2, limit 10 이면
                # offset=(2-1)*10 = 10
                offset = (page - 1) * limit
                
                # 3-2. 유저의 별점 데이터 조회
                ratings_list = await self.repo.get_ratings_data(user_pk, offset, limit)
            
            # 4. 페이지네이션 정보 생성
            pagination_info = PaginationInfo(
                current_page=page,
                total_pages=total_pages,
                total_count=total_count,
                limit=limit,
                has_next=page < total_pages,
                has_previous=page > 1
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
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
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
                        code=ErrorCode.NOT_FOUND,
                        message=Message.USER_NOT_FOUND
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
                offset = (page - 1) * limit
                
                # 3-2. 유저의 별점 데이터 조회
                bookmarks_list = await self.repo.get_bookmarks_data(user_pk, offset, limit)
            

            # 4. 페이지네이션 정보 생성
            pagination_info = PaginationInfo(
                current_page=page,
                total_pages=total_pages,
                total_count=total_count,
                limit=limit,
                has_next=page < total_pages,
                has_previous=page > 1
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
                    code=ErrorCode.INTERNAL_ERROR,
                    message=Message.INTERNAL_ERROR
                )
            )
        
    async def get_user_recommendations(self, user_pk: int) -> Union[UserRecommendationResponse, ErrorResponse]:
        """사용자 맞춤 피드(10개)와 키워드(8개)를 추천하는 핵심 서비스 메서드."""
        try:
            # user_pk = await self.repo.get_user_pk_by_user_id(user_id)
            if not user_pk:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.USER_NOT_FOUND))

            # --- Step 1: 추천의 'Seed'가 될 노드 ID 수집 ---
            seed_node_ids: List[str] = []
            is_personalized = True

            # 1순위: 최신 실시간 활동 (북마크/별점)
            latest_activity_feeds = await self.repo.get_latest_user_activities(user_pk)
            if latest_activity_feeds:
                seed_node_ids.extend([f"feed_{fid}" for fid in latest_activity_feeds])

            # 2순위: 누적된 검색 기록 (1순위 데이터가 부족할 경우 보충)
            if len(seed_node_ids) < 5:
                searched_keywords = await self.repo.get_user_searched_keywords(user_pk)
                if searched_keywords:
                    seed_node_ids.extend([f"keyword_{kw}" for kw in searched_keywords])
            
            # 3순위: 폴백 로직 (Seed가 전혀 없는 경우)
            if not seed_node_ids:
                is_personalized = False
                popular_feeds = await self.repo.get_popular_feeds_for_fallback()
                if not popular_feeds: # 인기 피드조차 없으면 빈 결과를 반환
                    return UserRecommendationResponse(data=UserRecommendationData(
                        is_personalized=False, recommended_feeds=[], recommended_keywords=[]
                    ))
                seed_node_ids.extend([f"feed_{fid}" for fid in popular_feeds])

            # --- Step 2: ML 모델로 유사 노드 확장 ---
            all_predictions = []
            # 여러 개의 Seed에서 나온 예측 결과를 하나로 합침
            for seed_node in set(seed_node_ids): # 중복된 씨앗 제거
                predictions = predict_similar_nodes(start_node_id=seed_node, top_n=30)
                all_predictions.extend(predictions)
            
            # 유사도 점수(내림차순) 기준으로 정렬 후 중복 제거
            all_predictions.sort(key=lambda x: x[1], reverse=True)
            unique_predictions: Dict[str, float] = {}
            for node_id, score in all_predictions:
                if node_id not in unique_predictions:
                    unique_predictions[node_id] = score

            # --- Step 3: 결과 정제 및 최종 응답 형태로 가공 ---
            recommended_feeds: List[RecommendedFeedItem] = []
            recommended_keywords: List[RecommendedKeywordItem] = []

            # ML 모델이 추천한 feed_id와 score를 별도로 추출
            predicted_feed_info: Dict[int, float] = {
                int(node_id.split('_')[1]): score
                for node_id, score in unique_predictions.items()
                if node_id.startswith('feed_')
            }
            
            if predicted_feed_info:
                feed_details_map = await self.repo.get_rich_feed_details_by_ids(list(predicted_feed_info.keys()))
            else:
                feed_details_map = {}

            # 예측된 키워드 목록 채우기 (최대 8개)
            predicted_keywords = [
                (node_id.split('_')[1], score)
                for node_id, score in unique_predictions.items()
                if node_id.startswith('keyword_')
            ]
            for keyword, score in predicted_keywords[:8]:
                recommended_keywords.append(RecommendedKeywordItem(keyword=keyword, score=round(score, 4)))

            # 상세 정보가 보강된 피드 추천 목록 채우기 (최대 10개)
            # ML 예측 점수 순으로 정렬된 ID를 기준으로 순회
            sorted_predicted_feeds = sorted(predicted_feed_info.items(), key=lambda item: item[1], reverse=True)

            for feed_id, score in sorted_predicted_feeds:
                if len(recommended_feeds) >= 10:
                    break
                
                details = feed_details_map.get(feed_id)
                if not details: continue # MySQL에서 상세 정보를 찾지 못하면 건너뜀

                recommended_feeds.append(RecommendedFeedItem(
                    id=details['id'],
                    title=details.get('title', ''),
                    summary=details.get('summary'),
                    organization_name=details.get('organization_name', '정보 없음'),
                    category_name=details.get('category_name', '정보 없음'),
                    published_date=details.get('published_date'),
                    score=round(score, 4),
                    view_count=details.get('view_count', 0),
                    average_rating=float(details.get('average_rating', 0.0)),
                    bookmark_count=details.get('bookmark_count', 0)
                ))
            
            response_data = UserRecommendationData(
                is_personalized=is_personalized,
                recommended_feeds=recommended_feeds,
                recommended_keywords=recommended_keywords
            )
            
            return UserRecommendationResponse(success=True, data=response_data)

        except Exception as e:
            logger.error(f"사용자 추천 생성 중 오류 발생 (user_pk: {user_pk}): {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))