from fastapi import APIRouter, Depends, HTTPException, Request, Response, Body
from fastapi.responses import JSONResponse

from app.F2_services.auth import AuthService, auth_handler
from app.F4_utils import device, cookie, client
from app.F5_core.security import JWTBearer
from app.F5_core.config import settings
from app.F5_core.dependencies import get_auth_service 
from app.F6_schemas import base
from app.F6_schemas.auth import (
    TokenResponse, TokenData, LoginRequest, LogoutRequest,
    UserCreate, RegisterSuccessResponse
)
router = APIRouter()

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