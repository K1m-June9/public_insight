from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
import logging

from app.F2_services.users import UserService
from app.F2_services.session import SessionService
from app.F5_core.dependencies import verify_active_user, get_user_service, get_session_service
from app.F5_core.redis import RedisCacheService
from app.F6_schemas import base
from app.F6_schemas.users import (
    UserProfile, UserProfileData, UserProfileResponse, UserNickNameUpdateRequest,
    UserPasswordUpdateRequest, UserPasswordUpdateResponse, UserRatingListResponse, 
    UserRatingListQuery, BookmarkItem, UserBookmarkListData, UserBookmarkListResponse, UserBookmarkListQuery
)
from app.F7_models.users import User

router = APIRouter()

logger = logging.getLogger(__name__)

# 사용자 프로필 조회 - 로그인 직후, 마이페이지
@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(verify_active_user),
    ):
    user_profile = UserProfile(
        user_id=current_user.user_id,
        nickname=current_user.nickname,
        email=current_user.email,
    )
    user_data = UserProfileData(user=user_profile)
    return UserProfileResponse(
        success=True,    
        data=user_data
    )    


# 사용자 프로필 수정 - 닉네임 변경
# 현재 아이디랑 이메일 수정은 없으므로 구체화 시켜서 표현하는게 좋다는 판단하에
# /api/v1/users/profile/nickname 으로 수정
# PUT: 전체 자원 교체
# PATCH: 일부 자원 수정
@router.patch("/profile/nickname", response_model=UserProfileResponse)
async def update_nickname(
    payload: UserNickNameUpdateRequest,
    current_user: User = Depends(verify_active_user),
    user_service: UserService = Depends(get_user_service)
    ):
    try: 
        # 1. nickname 규칙 및 중복 검사 후, ,업데이트 시도
        new_nickname = await user_service.update_nickname(current_user.user_id,payload.nickname)

        # 2. 닉네임이 None 또는 False일 경우, 유효성 실패 또는 중복된 닉네임
        if not new_nickname:
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="NICKNAME_INVALID_OR_DUPLICATE",
                    message="nickname이 중복되었거나 규칙에 맞지 않습니다",
                    details=None
                )
            )
            # 실패 반환
            return JSONResponse(status_code=400, content=error.model_dump())

        # 3. 닉네임 변경 성공 시, 사용자 캐시 무효화
        await RedisCacheService.invalidate_user_cache(current_user.user_id)
        
        # 4. 응답용 사용자 프로필 객체 생성
        new_profile = UserProfile(
            user_id=current_user.user_id,
            nickname=new_nickname,
            email=current_user.email,
        )
        user_data = UserProfileData(user=new_profile)
        
        # 5. 최종 응답 객체 생성 후 반환
        return UserProfileResponse(
            success=True,    
            data=user_data
        )
    
    except Exception as e:
        logger.exception("닉네임 변경 중 예외 발생")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    

# 비밀번호 변경
@router.put("/password", response_model=UserPasswordUpdateResponse)
async def update_password(
    request: Request,
    payload: UserPasswordUpdateRequest,
    current_user: User = Depends(verify_active_user),
    user_service: UserService = Depends(get_user_service),
    session_service: SessionService = Depends(get_session_service)
):  
    try:
        # 사용자 서비스에서 비밀번호 변경 시도
        result = await user_service.update_password(current_user.user_id,payload.current_password, payload.new_password)

        if not result:
            # 실패 시 에러 응답 구성 및 반환
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="PASSWORD_POLICY_VIOLATION",
                    message="기존 PASSWORD가 맞지 않거나 새로운 PASSWORD가 규칙에 맞지 않습니다",
                    details=None
                )
            )
            return JSONResponse(status_code=400, content=error.model_dump())

        # 비밀번호 변경 성공 : 사용자 캐시 무효화 (보안 목적)
        await RedisCacheService.invalidate_user_cache(current_user.user_id)

        # 현재 로그인 중인 세션을 제외한 모든 세션 로그아웃 처리
        refresh_token = request.cookies.get("refresh_token") or (
            (await request.json()).get("refresh_token") if request.method == "PUT" else None)
        

        # 미들웨어에서 주입된 인증 정보 추출
        jti = getattr(request.state, "jti", None)
        user_id = getattr(request.state, "user_id", None)   

        # 세션 서비스에 전달하여 나머지 세션 로그아웃 처리
        await session_service.logout_other_sessions(
            user_id=user_id, 
            current_jti=jti, 
            current_refresh_token=refresh_token)

        # 성공 응답 반환
        return UserPasswordUpdateResponse(
            success=True,
            message="비밀번호가 성공적으로 변경되었습니다"
        )
    except Exception as e:
        logger.exception("비밀번호 변경 중 예외 발생")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


# 사용자 별점 목록 조회
@router.get("/ratings", response_model=UserRatingListResponse)
async def get_my_ratings(
    query: base.PaginationQuery = Depends(),               # 페이지네이션 쿼리 파라미터
    current_user: User = Depends(verify_active_user),      # 현재 로그인한 사용자
    user_service: UserService = Depends(get_user_service), # UserService 의존성 주입
):
    # 쿼리 파라미터 객체 변환
    ratings_query =  UserRatingListQuery(
        page= query.page,
        limit = query.limit
    )

    # 서비스 호출하여 결과 가져오기
    result = await user_service.get_my_ratings(ratings_query, current_user.user_id)

    # 에러 응답 처리
    if isinstance(result, base.ErrorResponse):
        return JSONResponse(
            status_code=500,
            content=result.model_dump()
        )
    
    # 성공 응답 반환
    return result


# 사용자 북마크 목록 조회
@router.get("/bookmarks", response_model=UserBookmarkListResponse)
async def get_my_bookmarks(
    query: base.PaginationQuery = Depends(),
    current_user: User = Depends(verify_active_user),      # 현재 로그인한 사용자
    user_service: UserService = Depends(get_user_service), # UserService 의존성 주입
):
    # 쿼리 파라미터 객체 변환
    ratings_query =  UserBookmarkListQuery(
        page= query.page,
        limit = query.limit
    )

    # 서비스 호출하여 결과 가져오기
    result = await user_service.get_my_bookmarks(ratings_query, current_user.user_id)

        # 에러 응답 처리
    if isinstance(result, base.ErrorResponse):
        return JSONResponse(
            status_code=500,
            content=result.model_dump()
        )
    
    # 성공 응답 반환
    return result
