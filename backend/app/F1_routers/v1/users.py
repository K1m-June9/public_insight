from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
import logging

from app.F2_services.users import UserService
from app.F5_core.dependencies import verify_active_user, get_user_service
from app.F5_core.logging_decorator import log_event_detailed
from app.F5_core.redis import RedisCacheService
from app.F7_models.users import User
from app.F6_schemas.base import (
    ErrorResponse,
    ErrorCode,
)

from app.F6_schemas.users import (
    UserProfile,
    UserProfileData, 
    UserProfileResponse, 
    UserNickNameUpdateRequest,
    UserPasswordUpdateRequest, 
    UserPasswordUpdateResponse, 
    UserRatingListResponse, 
    UserRatingListQuery, 
    UserBookmarkListResponse, 
    UserBookmarkListQuery,
    UserRecommendationResponse
)


logger = logging.getLogger(__name__)

router = APIRouter()


# 사용자 프로필 조회 - 로그인 직후, 마이페이지, + 내 정보 조회
# - 미들웨어가 기본 접근 로그를 자동으로 남김, 추가 로그 코드 x
@router.get("/me", response_model=UserProfileResponse)
@log_event_detailed(action="READ", category=["USER", "PROFILE", "ME"])
async def get_my_profile(
    request: Request,
    current_user: User = Depends(verify_active_user),
    ):
    return UserProfileResponse(
        success=True,
        data=UserProfileData(
            user=UserProfile(
                user_id=current_user.user_id,
                nickname=current_user.nickname,
                email=current_user.email,
                role = current_user.role
                )
            )
        )



# 사용자 프로필 수정 - 닉네임 변경
# 현재 아이디랑 이메일 수정은 없으므로 구체화 시켜서 표현하는게 좋다는 판단하에
# /api/v1/users/me/nickname 으로 수정
# PUT: 전체 자원 교체
# PATCH: 일부 자원 수정
@router.patch("/me/nickname", response_model=UserProfileResponse)
@log_event_detailed(action="UPDATE", category=["USER", "PROFILE", "NICKNAME"])
async def update_nickname(
    request: Request,
    payload: UserNickNameUpdateRequest,
    current_user: User = Depends(verify_active_user),
    user_service: UserService = Depends(get_user_service)
    ):
    # 1. nickname 규칙 및 중복 검사 후, 업데이트 시도
    # user_service.update_nickname 함수 내부에서 상세한 DEBUG, WARNING 로그를 남길 수 있음
    result = await user_service.update_nickname(
        current_user.user_id,
        current_user.email,
        payload.nickname,
        current_user.role 
        )

    # 2. Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        if result.error.code in (ErrorCode.VALIDATION_ERROR, ErrorCode.DUPLICATE):
            status_code = 400
        elif result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 3. nickname 변경 성공 시, 사용자 캐시 무효화
    await RedisCacheService.invalidate_user_cache(current_user.user_id)

    return result

# =================================
# 사용자 맞춤 추천
# =================================
@router.get("/me/recommendations", response_model=UserRecommendationResponse)#@log_event_detailed(action="LIST", category=["USER", "RECOMMENDATION"])
async def get_my_recommendations(
    current_user: User = Depends(verify_active_user),
    user_service: UserService = Depends(get_user_service),
):
    """
    현재 로그인한 사용자를 위한 맞춤 피드 및 키워드를 추천함.
    - 사용자의 활동(북마크, 별점, 검색)이 있으면 개인화 추천을 제공.
    - 활동이 없으면 인기 피드 기반의 일반 추천을 제공.
    """
    # 2단계에서 구현할 서비스 로직을 호출함 
    result = await user_service.get_user_recommendations(current_user.id)
    
    # 2단계에서 구현할 에러 처리 로직 (현재는 기본 구조만 작성)
    if isinstance(result, ErrorResponse):
        status_code = 500 # 기본값
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 404
        return JSONResponse(status_code=status_code, content=result.model_dump())

    return result



# 비밀번호 변경
@router.put("/password", response_model=UserPasswordUpdateResponse)
@log_event_detailed(action="UPDATE", category=["USER", "PROFILE", "PASSWORD"])
async def update_password(
    request: Request,
    payload: UserPasswordUpdateRequest,
    current_user: User = Depends(verify_active_user),
    user_service: UserService = Depends(get_user_service),
):  
    # 1. 요청에서 세션 식별 정보(jti, refresh_token) 추출
    refresh_token = request.cookies.get("refresh_token") or ((await request.json()).get("refresh_token") if request.method == "PUT" else None)
    
    jti = getattr(request.state, "jti", None)

    # 2. password 변경 후 후속 조치 처리
    result = await user_service.update_password(
        user_id=current_user.user_id,
        current_password=payload.current_password, 
        new_password=payload.new_password,
        current_jti=jti,
        current_refresh_token=refresh_token
    )
    
    # 1-1. Service에서 에러 응답이 반환된 경우 처리
    if isinstance(result, ErrorResponse):
        status_code = 400
        if result.error.code == ErrorCode.INTERNAL_ERROR:
            status_code = 500
        elif result.error.code == ErrorCode.INVALID_PARAMETER:
            status_code = 401
        return JSONResponse(status_code=status_code, content=result.model_dump())

    return result



# 사용자 별점 목록 조회
@router.get("/ratings", response_model=UserRatingListResponse)
@log_event_detailed(action="LIST", category=["USER", "MY_ACTIVITY", "RATING"])
async def get_my_ratings(
    query: UserRatingListQuery = Depends(),               # 페이지네이션 쿼리 파라미터
    current_user: User = Depends(verify_active_user),      # 현재 로그인한 사용자
    user_service: UserService = Depends(get_user_service), # UserService 의존성 주입
):
    # # 쿼리 파라미터 객체 변환
    # ratings_query =  UserRatingListQuery(
    #     page= query.page,
    #     limit = query.limit
    # )

    # 서비스 호출하여 결과 가져오기
    result = await user_service.get_my_ratings(query, current_user.user_id)

    # 에러 응답 처리
    if isinstance(result, ErrorResponse):
        status_code = 500
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 응답 반환
    return result



# 사용자 북마크 목록 조회
@router.get("/bookmarks", response_model=UserBookmarkListResponse)
@log_event_detailed(action="LIST", category=["USER", "MY_ACTIVITY", "BOOKMARK"])
async def get_my_bookmarks(
    query: UserBookmarkListQuery = Depends(),
    current_user: User = Depends(verify_active_user),      # 현재 로그인한 사용자
    user_service: UserService = Depends(get_user_service), # UserService 의존성 주입
):
    # # 쿼리 파라미터 객체 변환
    # ratings_query =  UserBookmarkListQuery(
    #     page= query.page,
    #     limit = query.limit
    # )

    # 서비스 호출하여 결과 가져오기
    result = await user_service.get_my_bookmarks(query, current_user.user_id)

        # 에러 응답 처리
    if isinstance(result, ErrorResponse):
        status_code = 500
        if result.error.code == ErrorCode.NOT_FOUND:
            status_code = 400
        return JSONResponse(status_code=status_code, content=result.model_dump())
    
    # 성공 응답 반환
    return result