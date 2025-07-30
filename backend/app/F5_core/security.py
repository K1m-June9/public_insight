from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jose import JWTError
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status
import logging
import uuid
import hashlib

from app.F5_core.config import settings
from app.F7_models.users import UserRole


logger = logging.getLogger(__name__)

# 비밀번호 해시 및 검증에 사용할 CryptContext 설정
pwd_context = CryptContext(
    schemes=["bcrypt"], # bcrypt 해시 알고리즘 사용
    deprecated="auto",  # 자동으로 오래된 해시 스킴 감지 및 경고
    bcrypt__rounds=10   # bcrypt 연산 라운드 수(운영:12, 개발:10)
)

class AuthHandler:
    def __init__(self):
        # JWT 토큰 생성 및 검증에 사용할 비밀 키와 알고리즘 설정
        self._secret_key = settings.JWT_SECRET_KEY
        self._algorithm = settings.JWT_ALGORITHM


    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """평문 비밀번호와 해시된 비밀번호를 비교하여 유효성을 검사하는 메서드"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            ###########로그 나중에 수정#############
            logger.error(f"Password verification failed: {str(e)}")
            return False


    @staticmethod
    def get_password_hash(password: str) -> str:
        # 비밀번호를 bcrypt 해시로 암호화하여 반환
        return pwd_context.hash(password)


    def create_access_token(
        self,
        data: Dict[str, Any],
        token_type: str = "access",
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """JWT Acess Token 생성"""
        to_encode = data.copy()

        # Jti (토큰 고유 ID)가 없으면 새 UUID 생성
        if "jti" not in to_encode:
            to_encode["jti"] = str(uuid.uuid4())

        # role 값이 UserRole enum일 경우 문자열 값으로 반환
        if "role" in to_encode and isinstance(to_encode["role"], UserRole):
            to_encode["role"] = to_encode["role"].value

        now = datetime.utcnow()
        expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({
            "exp": expire,  # 만료 시간
            "iat": now,     # 발급 시간
            "type": token_type  # 토큰 타입 명시
        })

        # JWT 인코딩 및 반환
        return jwt.encode(to_encode, self._secret_key, algorithm=self._algorithm)


    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT 토큰 디코딩 및 검증"""
        try:
            payload = jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                options={
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_signature": True
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("토큰이 만료되었습니다.")
            return None
        except jwt.InvalidTokenError as e:
            logger.info(f"유효하지 않은 토큰입니다: {str(e)}")
            return None

    @staticmethod
    def generate_device_fingerprint(user_agent: Optional[str], ip_address: Optional[str]) -> str:
        """디바이스 지문 생성 함수"""
        ua = user_agent or ""   # User-Agent가 없으면 빈 문자열
        ip = ip_address or ""   # IP 주소가 없으면 빈 문자열
        fingerprint_source = f"{ua}:{ip}"   # User-Agent와 IP를 ':'로 결합
        return hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest() # SHA-256 해시 반환
    
    # 임시방편코드 - 리팩토링할 때 우리 스타일로 맞춰놓을게
    def decode_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        JWT Refresh Token을 디코딩하여 payload를 반환합니다.
        
        이 함수는 토큰이 변조되지 않았는지(서명 검증)만 확인합니다.
        만료 시간은 검증하지 않습니다. 왜냐하면 어차피 DB에서 존재 여부를
        확인하여 최종 유효성을 판단할 것이기 때문입니다.
        
        실패 시 예외를 발생시킵니다.
        """
        try:
            # 리프레시 토큰을 생성할 때 사용한 것과 동일한 비밀 키를 사용해야 합니다.
            payload = jwt.decode(
                token,
                self._refresh_secret_key, # 리프레시 토큰용 비밀 키
                algorithms=[self._algorithm],
                # 만료 시간(exp) 검증은 하지 않음
                options={"verify_exp": False, "verify_signature": True} 
            )
            return payload
        except JWTError as e:
            # 토큰이 깨졌거나, 서명이 위조되었거나, 형식이 잘못된 경우
            logger.warning(f"Refresh token decoding failed: {e}")
            raise JWTError("Invalid or malformed refresh token.") from e






# JWTBearer 미들웨어
# JWT 토큰을 Bearer 인증 헤더에서 검증하는 FastAPI 보안 클래스
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, auth_handler: Optional[AuthHandler] = None):
        super().__init__(auto_error=auto_error)
        self.auth_handler = auth_handler or AuthHandler()

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        # 상위 클래스 호출하여 Authorization 헤더 파싱
        credentials = await super().__call__(request)

        if not credentials or credentials.scheme != "Bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 스킴이 잘못되었습니다. Bearer 토큰을 사용하세요.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        # JWT 토큰 디코딩 및 검증
        payload = self.auth_handler.decode_access_token(credentials.credentials)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었거나 유효하지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"}
            )


        # 토큰 타입이 access가 아닌 경우 예외 처리
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 토큰 타입입니다.",
                headers={"WWW-Authenticate": "Bearer"}
            )


        # 사용자 ID(sub) 필수 검증
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 사용자 정보입니다.",
                headers={"WWW-Authenticate": "Bearer"}
            )


        # request.state에 인증 정보 저장(라우터 등에서 사용 가능)
        request.state.user_id = user_id
        request.state.jti = payload.get("jti")

        # role 정보가 UserRole enum 타입으로 변환 가능하면 변환, 아니면 기본 USER 역할 부여
        role_value = payload.get("role", UserRole.USER.value)
        try:
            request.state.role = UserRole(role_value)
        except ValueError:
            request.state.role = UserRole.USER

        # 최종적으로 토큰 문자열 반환 (필요 시)
        return credentials.credentials

# 싱글톤 인스턴스 생성
auth_handler = AuthHandler()
