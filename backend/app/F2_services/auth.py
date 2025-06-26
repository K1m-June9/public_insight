from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
import uuid
import random
from fastapi import HTTPException, status, Depends

from app.F3_repositories.auth import AuthRepository
from app.F4_utils.validators import validate_user_id, validate_password, validate_email
from app.F5_core.config import settings
from app.F5_core.security import auth_handler
from app.F5_core.redis import RedisManager
from app.F5_core.logger import logger
from app.F6_schemas import base
from app.F6_schemas import auth
from app.F7_models.users import User, UserStatus
from app.F7_models.refresh_token import RefreshToken



class AuthService:
    def __init__(self, repo: AuthRepository):
        # AuthRepository 인스턴스를 주입받아 DB 접근에 사용
        self.repo = repo


    async def authenticate_user(self, user_id: str, password: str) -> Union[User, base.ErrorResponse]:
        """주어진 사용자 ID와 비밀번호를 검증하여 인증을 수행합니다."""

        # 1. 사용자 정보를 DB에서 조회
        user = await self.repo.get_user_by_user_id(user_id)

        # 2. 사용자 없거나 비밀번호 불일치 시 실패 처리
        if not user or not auth_handler.verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt for user: {user_id}")
            return base.ErrorResponse(
                error=base.ErrorDetail(
                    code="INVALID_CREDENTIALS",
                    message=base.Message.LOGIN_FAILED,
                    detail=None
                )
            )
        
        # 3. 계정 상태가 활성화(ACTIVE)가 아니면 로그인 거부
        if user.status != UserStatus.ACTIVE:
            logger.warning(f"Inactive account access attempt: {user_id} (Status: {user.status})")
            return base.ErrorResponse(
                error=base.ErrorDetail(
                    code="INACTIVE_ACCOUNT",
                    message="계정이 활성화되지 않았습니다",
                    details={"status": user.status.value}
                )
            )
        
        # 4. 인증 성공: 사용자 객체 반환
        return user

    async def create_tokens(self, user: User, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 로그인 성공 후 토큰 생성 및 관리"""
        
        # device_info에서 user_agent와 ip_address 추출하여 디바이스 지문 생성
        device_id = auth_handler.generate_device_fingerprint(
            device_info.get("user_agent"),
            device_info.get("ip_address")
        )

        # 같은 유저, 같은 디바이스에 발급된 기존 Refresh Token 모두 무효화 처리
        await self.repo.revoke_device_refresh_tokens(user.user_id, device_id)

        # 새로운 Access Token 생성과 고유 식별자(jti) 생성
        access_token, jti = await self._generate_access_token(user)

        # 새로운 Refresh Token 후 DB에 저장
        refresh_token = await self._generate_refresh_token(user.user_id, device_id)

        logger.info(f"New tokens issued for {user.user_id} on device {device_id[:8]}")
        
        # 토큰 및 관련 정보 반환
        return {
            "access_token": access_token,
            "refresh_token": refresh_token.token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "device_id": device_id
        }



    async def refresh_access_token(self, refresh_token: str, device_info: Dict[str, Any]) -> Union[Dict[str, Any], base.ErrorResponse]:
        """Refresh Token을 이용해 Access Token 갱신 처리"""
        db_token: Optional[RefreshToken] = None  # 사전 선언 (안전하게)

        try:
            # 1. 디바이스 지문 생성
            device_id = auth_handler.generate_device_fingerprint(
                device_info.get("user_agent"),
                device_info.get("ip_address")
            )
            logger.debug(f"[refresh] device_id: {device_id}")

            # 2. Refresh Token을 DB에서 조회
            db_token = await self.repo.get_refresh_token(refresh_token, device_id)

            # 3. 존재 여부 확인
            if not db_token:
                logger.warning(f"Invalid refresh token: {refresh_token[:8]}..., device_id={device_id[:8]}")
                return base.ErrorResponse(
                    error=base.ErrorDetail(
                        code="INVALID_REFRESH_TOKEN",
                        message="유효하지 않은 리프레시 토큰입니다",
                        details=None
                    )
                )

            # 4. 무효화 여부 확인
            if db_token.revoked:
                logger.warning(f"Revoked refresh token reuse: {refresh_token}")
                await self._handle_token_reuse(db_token.user_id, refresh_token)

            # 5. 만료 여부 확인
            if db_token.expires_at < datetime.utcnow():
                logger.warning(f"Expired refresh token: {refresh_token[:8]}...")
                return base.ErrorResponse(
                    error=base.ErrorDetail(
                        code="INVALID_REFRESH_TOKEN",
                        message="만료된 리프레시 토큰입니다",
                        details=None
                    )
                )

            # 6. 사용자 조회
            user = await self.repo.get_user_by_user_id(db_token.user_id)
            if not user:
                logger.error(f"User not found: {db_token.user_id}")
                return base.ErrorResponse(
                    error=base.ErrorDetail(
                        code="INVALID_REFRESH_TOKEN",
                        message="사용자를 찾을 수 없습니다",
                        details=None
                    )
                )

            # 7. Access Token 재발급
            access_token, jti = await self._generate_access_token(user)

            # 8. 사용 시각 갱신
            await self._update_token_usage(db_token)

            return {
                "access_token": access_token,
                "refresh_token": db_token.token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "device_id": device_id
            }

        except HTTPException:
            raise

        except Exception as e:
            logger.error(f"Unexpected error in refresh_access_token: {e}", exc_info=True)
            if 'db_token' in locals() and db_token:
                logger.error(f"User not found: {db_token.user_id}")
            return base.ErrorResponse(
                error=base.ErrorDetail(
                    code="INTERNAL_SERVER_ERROR",
                    message="서버 내부 오류가 발생했습니다",
                    details=None
                )
            )




    async def logout(self, jti: str, user_id: str, refresh_token: str, device_id: str):
        try:
            """현재 디바이스 로그아웃"""
            # 로그아웃 시작 로그 기록
            logger.info(f"Logout started. jti={jti}, user_id={user_id}, refresh_token={refresh_token[:8] if refresh_token else None}")
            
            # Redis에서 해당 access token(jti) 삭제 처리
            await RedisManager.delete_access_token(jti)

            # user_id가 있을 경우, 해당 사용자의 토큰 키도 Redis에서 삭제
            if user_id:
                await RedisManager.delete_user_token_key(user_id, jti)
        except Exception as e:
            # Redis 작업 중 오류 발생 시 로그로 기록
            logger.error(f"Failed to delete access token in Redis: {e}")


        # refresh_token과 device_id가 모두 존재해야 로그아웃 처리 가능
        if refresh_token and device_id:
            # DB에서 refresh_token과 device_id로 토큰 존재 여부 조회
            token_in_db = await self.repo.get_refresh_token(refresh_token, device_id)

            # DB에 토큰이 없으면 유효하지 않은 refresh_token으로 판단, 예외 발생
            if not token_in_db:
                logger.warning("Invalid refresh token during logout.")
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            # 토큰이 유효하면 DB에서 해당 refresh_token 무효화 처리
            logger.info(f"Revoking refresh token: {refresh_token[:8]} on device {device_id}...")
            await self.repo.revoke_refresh_token(refresh_token, device_id)

            # 로그아웃 완료 로그 기록
            logger.info(f"Session terminated for token: {jti[:8]}...")
        else:
            # refresh_token 또는 device_id가 없으면 로그아웃 불가, 경고 로그 및 예외 발생
            logger.warning("Refresh token or device_id missing during logout.")
            raise HTTPException(status_code=401, detail="Refresh token or device_id missing")





    async def logout_all_devices(self, user_id: str) -> None:
        """해당 사용자의 모든 디바이스 세션 종료 처리"""
        # 1. DB 내 해당 사용자의 모든 RefreshToken 무효화
        await self.repo.revoke_all_user_refresh_tokens(user_id)
        
        # 2. Redis에서 user_tokens 패턴으로 저장된 모든 키를 SCAN하며 검색 및 삭제
        cursor = 0
        pattern = f"user_tokens:{user_id}:*"
        while True:
            cursor, keys = await RedisManager.scan_keys(cursor=cursor, pattern=pattern)
            if keys:
                # 검색된 키들 삭제
                await RedisManager.delete_keys(keys)
            # SCAN 커서가 "0"이면 모든 키 검색 완료
            if cursor == "0"or cursor == b"0":
                break
        
        # 3. 로그아웃 완료 로그 기록
        logger.info(f"All sessions terminated for user: {user_id}")



    # ======== 내부 헬퍼 함수들 ========
    async def _generate_access_token(self, user: User) -> tuple[str, str]:
        """JWT Access Token 생성 및 Redis에 jti 저장 처리 함수"""
        try:
            jti = str(uuid.uuid4()) # 고유 토큰 식별자 생성
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) # 토큰 만료시간 설정
            ttl = int(access_token_expires.total_seconds()) # 만료 시간을 초단위로 변환
            
            # JWT Access Token 생성 (payload에 user_id, role, jti 포함)
            access_token = auth_handler.create_access_token(
                data={"sub": user.user_id, "role": user.role.value, "jti": jti}, expires_delta=access_token_expires,
            )

            # Redis에 토큰 유효성 관리를 위한 jti 저장 (토큰 만료 시간과 동일하게 설정)
            await RedisManager.set_access_token(jti, user.user_id, ttl)
            # 사용자별 토큰 키 관리용 Redis 저장
            await RedisManager.set_user_token_key(user.user_id, jti, ttl)
            
            return access_token, jti
        except Exception as e:
            logger.error(f"Failed to generate access token or store in Redis: {e}", exc_info=True)
            raise


    async def _generate_refresh_token(self, user_id: str, device_id: str) -> RefreshToken:
        """
        Refresh Token 생성 후 DB 저장.
        - UUID 토큰 생성
        - 만료시간 설정
        - revoked = False (초기상태)
        - last_used_at = 현재시간
        """
        refresh_token = RefreshToken(
            user_id=user_id,
            device_id=device_id,
            token=RefreshToken.generate_token(),
            expires_at=RefreshToken.generate_token_expiry(),
            revoked=False,
            last_used_at=datetime.utcnow()
        )
        await self.repo.add_refresh_token(refresh_token)
        return refresh_token


    async def _update_token_usage(self, token: RefreshToken) -> None:
        """Refresh Token 사용 시각 갱신하는 함수"""

        token.last_used_at = datetime.utcnow()
        try:
            self.repo.db.add(token)     # 변경된 토큰 객체를 DB 세션에 추가
            await self.repo.db.commit() # 변경사항 커밋
        except Exception as e:
            await self.repo.db.rollback()   # 커밋 실패 시 롤백
            logger.error(f"Failed to update RefreshToken usage timestamp: {e}")
            raise


    async def _handle_token_reuse(self, user_id: str, token: str) -> None:
        """Refresh Token 재사용 감지되었을 때 보안상 대응하는 함수"""

        # 1. 모든 디바이스 로그아웃 처리(세션 모두 종료)
        await self.logout_all_devices(user_id)

        # 2. 심각 로그 기록(보안경고)
        logger.critical(f"Token reuse detected! User: {user_id}, Token: {token[:8]}...")

        # 3. 예외 발생(클라이언트에게 알림) ***수정***
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security alert: Token reuse detected. All sessions terminated."
        )


    async def is_user_id_available(self, user_id: str) -> bool:
        """user_id 중복 및 유효성 검사"""
        # 유효성 검사
        if not validate_user_id(user_id):
            logger.info(f"User ID validation failed: {user_id}")
            return False

        # 중복 검사
        exists = await self.repo.is_user_id_exists(user_id)
        logger.info(f"User ID exists check: {user_id} => {exists}")
        return not exists
    
    async def is_email_available(self, email: str) -> bool:
        """email 중복 여부 검사"""
        # 이메일 형식 검사
        if not validate_email(email):
            logger.info(f"이메일 형식 오류: {email}")
            return False 

        # 이메일 DB 중복 검사
        exists = await self.repo.is_email_exists(email)
        return not exists
    
    async def validate_password_rule(self, password: str) -> bool:
        """password 규칙 검사"""
        if not validate_password(password):
            return False
        return True 
    
    async def assign_initial_nickname(self, user_id: str) -> str:
        """초기 닉네음은 user_id로 설정, 중복 시 난수를 붙여서 닉네임 생성"""
        base_nickname = user_id
        if not await self.repo.is_nickname_exists(base_nickname):
            return base_nickname 
        
        for _ in range(5):
            candidate = f"{base_nickname}{random.randint(100, 9999)}"
            if not await self.repo.is_nickname_exists(candidate):
                return candidate
            
        logger.error(f"닉네임 중복으로 인해 자동 생성 실패")
        raise ValueError("닉네임 자동 생성 실패: 중복된 값이 너무 많습니다.")
            
    
    async def create_user(self, credentials: auth.UserCreate) -> User:
        hashed_pw = auth_handler.get_password_hash(credentials.password)

        logger.info(f"생성하기 중")
        new_user = User(
            user_id=credentials.user_id,
            password_hash=hashed_pw,
            email=credentials.email,
            nickname=credentials.nickname,
            terms_agreed=credentials.terms_agreed,
            privacy_agreed=credentials.privacy_agreed,
            notification_agreed=credentials.notification_agreed,
            terms_agreed_at=datetime.utcnow() if credentials.terms_agreed else None,
            privacy_agreed_at=datetime.utcnow() if credentials.privacy_agreed else None,
            marketing_agreed_at=datetime.utcnow() if credentials.notification_agreed else None,
        )

        await self.repo.save_user(new_user)
        return new_user
