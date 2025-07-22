from fastapi import APIRouter, Depends, HTTPException, Request, Response, Body, BackgroundTasks, status
from fastapi.responses import JSONResponse
import logging 

from app.F2_services.session import SessionService
from app.F2_services.auth import AuthService, auth_handler
from app.F4_utils import device, cookie, client
from app.F4_utils.email import EmailVerificationService, SendPasswordResetEmail
from app.F5_core.redis import PasswordResetRedisService
from app.F5_core.security import JWTBearer
from app.F5_core.config import settings
from app.F5_core.dependencies import (
    get_auth_service, get_email_verification_services,
    get_password_reset_redis_service, get_session_service
)
from app.F6_schemas import base
from app.F6_schemas.auth import (
    TokenResponse, TokenData, LoginRequest, LogoutRequest,
    UserCreate, RegisterSuccessResponse, UserCheckID, UserCheckEmail,
    EmailSendSuccessResponse, EmailVerifyCode, EmailVerifySuccessResponse,
    FindIdResponse, ResetPasswordRequest, PasswordResetEmailSentResponse,
    TokenVerificationResponse, PasswordResetCompleteResponse, PasswordResetSubmitRequest,
)
router = APIRouter()

logger = logging.getLogger(__name__)

# 로그인 엔드포인트
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,               # 요청 객체(클라이언트 정보, 헤더, IP 등 확인용)
    credentials: LoginRequest,      # 사용자 입력 데이터(user_id, password)
    response: Response,             # 응답 객체(쿠키 설정 등)
    auth_service: AuthService = Depends(get_auth_service) # AuthService 인스턴스 주입
):
    # 1. 사용자 인증 처리(아이디, 비밀번호 확인 + 사용자 상태 검사 포함)
    user_or_error = await auth_service.authenticate_user(credentials.user_id, credentials.password)

    # 2. 인증 실패 시 ErrorResponse 반환 여부 확인
    if isinstance(user_or_error, base.ErrorResponse):
        # 에러 코드에 따라 HTTP 상태코드 설정(401: 인증 실패, 403: 계정 비활성화)
        status_code = status_code = 401 if user_or_error.error.code == "INVALID_CREDENTIALS" else 403
        return JSONResponse(status_code=status_code, content=user_or_error.model_dump())

    user = user_or_error

    # 3. 사용자 디바이스 정보 수집(User-Agent 헤더, 클라이언트 IP)
    device_info = device.extract_device_info(request)

    # 4. 인증 성공 시 Access Token과 Refresh Token 생성
    tokens = await auth_service.create_tokens(user, device_info)

    # 5. 클라이언트 유형 판단
    is_mobile = client.is_mobile_client(request)

    # 6. Refresh Token을 HttpOnly 쿠키로 설정(보안 및 경로 제한 포함)
    if not is_mobile:
        # 웹: Refresh Token을 쿠키에 설정
        cookie.set_refresh_token_cookie(response, tokens["refresh_token"])
        refresh_token = None
    else:
        # 앱: JSON body에 포함
        refresh_token = tokens["refresh_token"]

    # 7. 응답 반환
    return TokenResponse(
        message=base.Message.LOGIN_SUCCESS,
        data=TokenData(
            access_token=tokens["access_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            refresh_token=refresh_token # 웹은 None
        )
    )


# 리프레쉬
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):
    # 1. 쿠키 또는 JSON에서 refresh_token 추출
    # 웹 브라우저 -> 쿠키에서 추출
    # 모바일 웹 -> JSON body에서 추출
    refresh_token = request.cookies.get("refresh_token") or (
        (await request.json()).get("refresh_token") if request.method == "POST" else None
    )

    if not refresh_token:
        error = base.ErrorResponse(
            error = base.ErrorDetail(
                code="REFRESH_TOKEN_REQUIRED",
                message="리프레시 토큰이 누락되었습니다",
                details=None
            )
        )
        return JSONResponse(status_code=401, content=error.model_dump())

    # 2. 디바이스 정보 추출
    device_info = device.extract_device_info(request)

    # 3. 토큰 갱신 처리
    try:
        tokens_or_error = await auth_service.refresh_access_token(refresh_token, device_info)
    except HTTPException as e:
        response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
        raise e

    # 4. 실패 시 ErrorResponse를 JSONResponse로 반환
    if isinstance(tokens_or_error, base.ErrorResponse):
        status_code = 401 if tokens_or_error.error.code == "INVALID_REFRESH_TOKEN" else 403
        return JSONResponse(status_code=status_code, content=tokens_or_error.model_dump())

    
    tokens = tokens_or_error

    # 5. 클라이언트 유형 판단
    is_mobile = client.is_mobile_client(request)

    # 6. Refresh Token을 HttpOnly 쿠키로 설정(보안 및 경로 제한 포함)
    if not is_mobile:
        # 웹: Refresh Token을 쿠키에 설정
        cookie.set_refresh_token_cookie(response, tokens["refresh_token"])
        refresh_token = None
    else:
        # 앱: JSON body에 포함
        refresh_token = tokens["refresh_token"]

    # 7. 응답 반환
    return TokenResponse(
        message=base.Message.SUCCESS,
        data=TokenData(
            access_token=tokens["access_token"],
            token_type="bearer",
            expires_in=tokens["expires_in"],
            refresh_token=refresh_token # 웹은 None
        )
    )


# 로그아웃(현재 디바이스)
@router.post("/logout", response_model=None)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(JWTBearer()),
):  
    # 1. 요청 본문에서 필요한 정보 추출
    refresh_token = request.cookies.get("refresh_token") or (
        (await request.json()).get("refresh_token") if request.method == "POST" else None)
    
    # 2. devcie_id 추출
    device_info = device.extract_device_info(request)
    device_id = auth_handler.generate_device_fingerprint(
        device_info.get("user_agent"),
        device_info.get("ip_address")
    )


    # 3. 요청 상태에서 jti, user_id 추출
    jti = getattr(request.state, "jti", None)
    user_id = getattr(request.state, "user_id", None)


    # 4. 필수 정보 없을 경우 예외 처리
    if not (refresh_token and device_id and jti and user_id):
        error = base.ErrorResponse(
            error=base.ErrorDetail(
                code="REFRESH_TOKEN_REQUIRED",
                message="리프레시 토큰, device_id, jti 또는 user_id가 누락되었습니다",
                details=None
            )
        )
        return JSONResponse(status_code=401, content=error.model_dump())


    # 5. 로그아웃 처리
    try:
        await auth_service.logout(
            jti=jti,
            user_id=user_id,
            refresh_token=refresh_token,
            device_id=device_id
        )
    except HTTPException as e:
        # 실패 시 쿠키 제거 후 예외 전달
        response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
        raise e


    # 6. 성공 시 쿠키 제거 및 응답 반환
    response.delete_cookie("refresh_token", path="/api/v1/auth/refresh")
    return base.SuccessResponse()




# 회원가입 완료 버튼
@router.post("/register",response_model=RegisterSuccessResponse)
async def register(
    request: Request,
    credentials: UserCreate,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service)
):  
    try:
        # 1. 필수 이용약관 동의 확인
        if not (credentials.terms_agreed and credentials.privacy_agreed):
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="AGREEMENT_REQUIRED",
                    message="이용약관 및 개인정보 처리방침 동의는 필수입니다",
                    details=None
                )
            )
            return JSONResponse(status_code=400, content=error.model_dump())


        # 2. user_id 중복 및 규칙 검사
        if not await auth_service.is_user_id_available(credentials.user_id):
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="USER_ID_INVALID_OR_DUPLICATE",
                    message="사용자 ID가 중복되었거나 규칙에 맞지 않습니다",
                    details=None
                )
            )
            return JSONResponse(status_code=400, content=error.model_dump())

        # 3. 이메일 중복 검사
        if not await auth_service.is_email_available(credentials.email):
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="EMAIL_INVALID_OR_DUPLICATE",
                    message="이메일이 중복되었거나 형식이 올바르지 않습니다",
                    details=None
                )
            )
            return JSONResponse(status_code=400, content=error.model_dump())


        # 4. 비밀번호 규칙 검사
        if not await auth_service.validate_password_rule(credentials.password):
            error = base.ErrorResponse(
                error = base.ErrorDetail(
                    code="PASSWORD_RULE_VIOLATION",
                    message="비밀번호가 규칙에 맞지 않습니다",
                    details=None
                )
            )
            return JSONResponse(status_code=400, content=error.model_dump())


        # 5. 초기 닉네임은 user_id로 설정
        credentials.nickname = await auth_service.assign_initial_nickname(credentials.user_id)


        # 6. 유저 생성
        user = await auth_service.create_user(credentials)

        # 7. 결과 반환 (UserResponse 스키마로 직렬화)
        return RegisterSuccessResponse(
            message="회원가입이 완료되었습니다" # 로그인 페이지로 이동
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # 콘솔에 전체 예외 출력
        return JSONResponse(status_code=500, content={"detail": str(e)})
    

# check-id 버튼
@router.post("/check-id", response_model=base.BaseResponse)
async def check_user_id_availability(
    request: UserCheckID,
    auth_service: AuthService = Depends(get_auth_service)
):
    # user_id 중복 및 규칙 검사
    if not await auth_service.is_user_id_available(request.user_id):
        return base.BaseResponse(success=False)
    
    return base.BaseResponse(success=True)


# 이메일 인증코드 [발송] 버튼
@router.post("/check-email/send", response_model=EmailSendSuccessResponse)
async def send_verification_code(
    request: UserCheckEmail,
    auth_service: AuthService = Depends(get_auth_service),
    email_service: EmailVerificationService = Depends(get_email_verification_services)
):
    # 1. user_id 중복 및 규칙 검사
    if not await auth_service.is_email_available(request.email):
        error = base.ErrorResponse(
            error = base.ErrorDetail(
                code="EMAIL_INVALID_OR_DUPLICATE",
                message="이메일이 중복되었거나 형식이 올바르지 않습니다",
                details=None
            )
        )
        return JSONResponse(status_code=400, content=error.model_dump())
    
    # 2. 인증코드 발송
    await email_service.send_code(request.email)
    return EmailSendSuccessResponse()


# 이메일 인증 코드 검증 [확인] 버튼
@router.post("/check-email/verify")
async def email_verify(
    valid: EmailVerifyCode,
    email_service: EmailVerificationService = Depends(get_email_verification_services)
):
    is_valid = await email_service.verify_code(valid.email, valid.code)

    if not is_valid:
        raise HTTPException(status_code=400, detail="인증 코드가 올바르지 않습니다")
    return EmailVerifySuccessResponse()


# 아이디 찾기 버튼
@router.post("/find-id", response_model=FindIdResponse)
async def find_user_id(
    payload: UserCheckEmail,
    auth_service: AuthService = Depends(get_auth_service)
):
    masked_user_id = await auth_service.find_user_id_by_email(payload.email)

    if masked_user_id:
        return FindIdResponse(
            message = "success",
            masked_user_id=masked_user_id
        )
    
    # 실패 시 : 보안 강화를 위해 동일 응답을 반환
    return FindIdResponse(
        message = "success",
        masked_user_id=""
    )


# 비밀번호 재설정 요청(이메일 + user_id 검증 후 토큰 생성 및 이메일 발송)
@router.post("/reset-password-reset", response_model=PasswordResetEmailSentResponse)
async def request_reset_password(
    payload: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
    ):
    """이메일과 user_id 일치 여부 확인 후 토큰 생성 및 이메일 발송"""
    success = await auth_service.handle_password_reset_request(payload.email, payload.user_id)

    if success:
        return PasswordResetEmailSentResponse(
            success=True, 
            message="비밀번호 재설정 메일이 전송되었습니다"
        )
    
    # 실패 시 : 보안 강화를 위해 동일 응답을 반환
    return PasswordResetEmailSentResponse(
        success=True,
        message = "입력하신 정보와 일치하는 계정을 찾을 수 없습니다"
    )


# 비밀번호 재설정 토큰 검사
@router.get("/verify-reset-token", response_model=TokenVerificationResponse)
async def verify_reset_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    비밀번호 재설정 토큰 유효성 검사 API
    - 사용자가 이메일로 받은 비밀번호 재설정 링크를 클릭하면, 해당 링크에 포함된 토큰의 유효성을 검증
    - 유효한 경우: 토큰에 연결된 사용자 정보(email, user_id)와 함께 valid=True 반환
    - 유효하지 않거나 만료된 경우: 400 Bad Request 예외 발생
    """
    # Redis에 저장된 토큰 정보 조회 및 유효성 검사
    token_data = await auth_service.verify_password_reset_token(token)

    if token_data:
        # 토큰이 유효할 경우: 연결된 이메일 및 user_id 반환
        return TokenVerificationResponse(
            valid=True, 
            email=token_data["email"],
            user_id=token_data["user_id"],
            message="유효한 토큰"
        )
    
    # 토큰이 존재하지 않거나 만료된 경우 예외 처리

    error = base.ErrorResponse(
        error = base.ErrorDetail(
            code="TOKEN_INVALID_OR_EXPIRED",
            message="토큰이 유효하지 않거나 만료되었습니다",
            details=None
            )
        )
    return JSONResponse(status_code=400, content=error.model_dump())



# 실제 비밀번호 재설정 수행
@router.post("/reset-password", response_model=PasswordResetCompleteResponse)
async def reset_password(
    payload: PasswordResetSubmitRequest, # 요청 본문: 토큰과 새 비밀번호를 포함
    auth_service: AuthService = Depends(get_auth_service),
    redis_service: PasswordResetRedisService = Depends(get_password_reset_redis_service),  # 의존성 추가
    session_service: SessionService = Depends(get_session_service)
):  
    # 비밀번호 재설정 수행 (토큰 유효성 검증 및 비밀번호 변경)
    result = await auth_service.reset_user_password(
        token=payload.token,
        new_password=payload.new_password,
        password_reset_redis_service=redis_service,  # Redis에서 토큰 조회 및 삭제
        session_service=session_service
    )

    # 토큰이 유효하지 않거나 만료될 경우 에러 응답 반환
    if not result:
        error = base.ErrorResponse(
            error=base.ErrorDetail(
                code="TOKEN_INVALID_OR_EXPIRED",
                message="유효하지 않거나 만료된 토큰입니다."
            )
        )
        return JSONResponse(status_code=400, content=error.model_dump())
    # 비밀번호 변경 성공 응답 반환
    return PasswordResetCompleteResponse(
        success=True,
        message="비밀번호가 성공적으로 재설정되었으며, 모든 기기에서 로그아웃 되었습니다"
    )
