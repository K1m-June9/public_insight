from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from typing import Set, Optional, Dict, Any, List
import logging 
import re

from app.F5_core.security import auth_handler
from app.F5_core.redis import RedisManager
from app.F5_core.logger import log_token_event
from app.F7_models.users import UserRole, UserStatus

logger = logging.getLogger(__name__)

class JWTBearerMiddleware(BaseHTTPMiddleware):
    """
    Access Token 기반 인증 미들웨어

    - Authorization 헤더에서 JWT를 추출 및 검증
    - Redis에서 토큰이 유효한지 확인 (jti 기반)
    - 사용자 계정 상태 확인 (비활성/차단된 계정 차단)
    - 경로별 Role 기반 접근 제한
    - 인증된 사용자 정보를 request.state에 주입
    """

    def __init__(
        self, app,
        *,
        exempt_paths: Optional[Set[str]] = None,
        exempt_regex_paths: Optional[List[str]] = None,
        admin_paths: Optional[Dict[str, Set[UserRole]]] = None,
    ):
        super().__init__(app)
        self.exempt_paths = exempt_paths or set()   # 인증 예외 경로들
        self.exempt_regex_paths = [re.compile(p) for p in (exempt_regex_paths or [])]
        self.admin_paths = admin_paths or {}        # 관리자 전용 경로와 권한 매핑

    async def dispatch(self, request: Request, call_next):
        # 1) 정적 경로 예외
        if request.url.path in self.exempt_paths:
            return await call_next(request)
        
        # 2) 동적 경로 예외(정규식 매칭)
        for pattern in self.exempt_regex_paths:
            if pattern.match(request.url.path):
                return await call_next(request)
        
        # 헤더 인증 여부 확인(새로추가)
        auth_header = request.headers.get("Authorization")

        if auth_header:
            try:
                # 1. Authorization 헤더에서 토큰 추출
                token = self._extract_token(request)

                # 2. 토큰 디코딩 및 기본 claim 검증
                payload = self._validate_token(token)

                # 3. Redis 기반 토큰 블랙리스트 확인 (jti)
                await self._verify_token_not_revoked(payload)

                # 4. Role 기반 경로 접근 권한 체크
                self._check_role_access(request, payload)

                # 5. 요청 컨텍스트에 인증된 사용자 정보 저장
                self._set_request_state(request, payload)

                return await call_next(request)

            except HTTPException as http_exc:
                logger.warning(f"Authentication failed: {http_exc.detail}")
                raise
        
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(f"Unexpected authentication error: {str(exc)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal authentication error"
            )


    def _extract_token(self, request: Request) -> str:
        """
        Authorization 헤더에서 Bearer 토큰 추출
        - Authorization: Bearer <JWT토큰>
        - 잘못된 형식 또는 누락 시 HTTP 401 예외 발생
        """

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header"
            )
        
        try:
            scheme, token = auth_header.split()

            # 인증 방식이 "bearer"가 아닌 경우 → 예: "Basic" 등 → 실패 처리
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
            
            # 토큰 문자열 반환
            return token
        except ValueError:
            # Authorization 헤더 형식이 잘못되었거나 split 실패한 경우
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )


    def _validate_token(self, token: str) -> Dict[str, Any]:
        """
        토큰 디코드 및 필수 클레임 존재 확인
        - 유효하지 않거나 만료된 토큰이면 401 Unauthorized 예외 발생
        """
        
        # [1] JWT 토큰 디코딩 시도(서명 검증 포함)
        payload = auth_handler.decode_access_token(token)

        # [2] 토큰이 유효하지 않거나 만료된 경우 -> 인증 실패
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )


        # [3] 필수 클레임들이 모두 존재하는지 확인
        #    - sub: 사용자 ID
        #    - role: 사용자 권한
        #    - jti: 토큰 고유 식별자 (revocation 체크용)
        required_claims = {'sub', 'role', 'jti'}
        if not required_claims.issubset(payload.keys()):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing required token claims"
            )

        #[4] 유효성 검사를 통과한 경우, 반환
        return payload


    async def _verify_token_not_revoked(self, payload: Dict[str, Any]) -> None:
        """
        Redis에 저장된 AccessToken JTI 키가 존재하는지 확인

        - JWT payload에서 고유 식별자 jti를 추출
        - 이 jti가 Redis에 존재하는지 확인하여 토큰이 아직 유효한지 검사
        - 존재하지 않으면 만료되었거나, 로그아웃/블랙리스트 처리를 거친 토큰으로 간주하고 인증 거부
        """

        jti = payload.get("jti") # JWT 토큰에서 'jti' 클레임 추출 (고유 식별자)
        exists = await RedisManager.get_access_token(jti)  # jti로 Redis에서 토큰 존재 확인
        if not jti or not exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token revoked or invalid"
            )

    def _check_role_access(self, request: Request, payload: Dict[str, Any]) -> None:
        """
        특정 경로에 Role 제한이 있는 경우 확인
        - self.admin_paths에 명시된 경로에 대해 사용자 권한이 충분한지 검사
        """

        # 현재 요청 경로에 요구되는 역할 집합 가져오기
        required_roles = self._get_required_roles(request)

        if required_roles:
            try:
                # JWT 토큰에서 추출한 사용자 역할을 Enum으로 변환
                user_role = UserRole(payload['role'])
            except ValueError:
                # 토큰에 정의된 역할 값이 UserRole Enum에 없는 경우 예외 처리
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user role"
                )
            
            # 사용자의 역할이 해당 경로에서 허용된 여갛ㄹ에 포함되지 않으면 접근 금지
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient privileges" # 권한 부족
                )

    def _get_required_roles(self, request: Request) -> Optional[Set[UserRole]]:
        """
        현재 요청 경로에 요구되는 역할(Role)을 반환
        - self.admin_paths 설정을 기반으로 경로 prefix와 일치하는 경우 그에 해당하는 역할 집합(Set[UserRole])을 반환
        - 일치하는 prefix가 없으면 None 반환 (즉, 역할 제한 없음)
        """
        for path_prefix, roles in self.admin_paths.items():
            # 요청 경로가 특정 prefix로 시작하는지 확인
            if request.url.path.startswith(path_prefix):
                return roles # 해당 경로에 요구되는 역할 반환
        return None  # 일치하는 경로 prefix가 없으면 제한된 역할 없음으로 처리

    def _set_request_state(self, request: Request, payload: Dict[str, Any]) -> None:
        """
        인증된 사용자 정보를 request.state에 저장
        - 이후 라우터, 서비스, 의존성 함수 등에서 request.state를 통해 사용자 정보를 조회할 수 있게 함
        """
        request.state.user_id = payload['sub']
        role_value = payload.get('role')
        if not role_value:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing user role in token"
            )
        try:
            request.state.role = UserRole(role_value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user role in token"
            )
        # 토큰의 고유 식별자 (jti)를 저장 - 추후 Redis 블랙리스트 처리 등에 활용
        request.state.jti = payload['jti']

        # 전체 토큰 payload도 통째로 저장해 필요 시 참조 가능
        request.state.token_payload = payload


"""
[인증 흐름 정리]
1. 클라이언트 → API 요청 시:
    Authorization: Bearer <Access Token>

2. JWTBearerMiddleware
    - 토큰 추출
    - jti 블랙리스트 확인 (Redis)
    - 토큰 디코드 및 유효성 검증
    - Role 권한 확인
    - request.state에 사용자 정보 저장

3. 이후 라우터나 서비스는 request.state.user_id 등으로 사용자 식별 가능
"""


"""
    async def _verify_user_status(self, payload: Dict[str, Any]) -> None:
        user_id = payload['sub']
        user = await self.auth_repo.get_user_by_user_id(user_id)
        if not user:
            # 사용자가 존재하지 않을 경우 예외 발생
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 사용자 상태가 "ACTIVE"가 아니면 인증 거부
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user.status.value}"
            )
"""