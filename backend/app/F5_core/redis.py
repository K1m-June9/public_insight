from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from redis.exceptions import RedisError
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from datetime import timedelta
import logging
import secrets
import json
from typing import Optional, Dict, Any, Callable, Awaitable
import os

from app.F7_models.users import User
from app.F5_core.config import settings

logger = logging.getLogger(__name__)

class RedisSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    IS_LOCAL: bool = True

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None

    CLIENT_REDIS_URL: Optional[str] = None
    EMAIL_REDIS_URL: Optional[str] = None
    TOKEN_REDIS_URL: Optional[str] = None
    PASSWORD_RESET_REDIS_URL: Optional[str] = None

    model_config = ConfigDict(
        env_file =  os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding = "utf-8",
        extra = "ignore",
    )

    def _default_base_url(self) -> str:
        host = self.REDIS_HOST or ("redis_server" if self.ENVIRONMENT == "production" and not self.IS_LOCAL else "localhost")
        port = self.REDIS_PORT or 6379
        return f"redis://{host}:{port}"

    def get_client_url(self) -> str:
        return self.CLIENT_REDIS_URL or f"{self._default_base_url()}/0"

    def get_email_url(self) -> str:
        return self.EMAIL_REDIS_URL or f"{self._default_base_url()}/1"

    def get_token_url(self) -> str:
        return self.TOKEN_REDIS_URL or f"{self._default_base_url()}/13"
    
    def get_password_reset_url(self) -> str:
        return self.PASSWORD_RESET_REDIS_URL or f"{self._default_base_url()}/14"


# 인스턴스 생성
redis_settings = RedisSettings()

# Redis 클라이언트 생성
client_redis = Redis.from_url(redis_settings.get_client_url())
email_redis = Redis.from_url(redis_settings.get_email_url())
token_redis = Redis.from_url(redis_settings.get_token_url())
password_reset_redis = Redis.from_url(redis_settings.get_password_reset_url())

# token_redis
class RedisManager:
    """
    Redis에 관련된 캐시 및 토큰 저장 기능을 모은 정적 유틸 클래스
    - access token 저장/조회/삭제
    - 사용자 정보 캐싱 및 무효화
    - 장애 대응 fallback 처리
    """

    @staticmethod
    async def set_access_token(jti: str, user_id: str, expire: int) -> None:
        """
        액세스 토큰의 고유 식별자(jti)를 Redis에 저장하는 함수
        목적
        - API 요청 시 Access Token jti의 유효성 검증을 위해 사용
        - Redis에 jti가 없으면 토큰이 만료되었거나 무효화된 것으로 간주하여 블랙리스트 기능 수행
        """
        await token_redis.setex(f"access_token:{jti}", expire, user_id)

    
    @staticmethod
    async def set_user_token_key(user_id: str, jti: str, expire: int) -> None:
        """
        특정 사용자가 발급받은 Access Token의 jti를 Redis에 저장하는 함수
        목적:
        - 특정 사용자의 모든 토큰을 추적하여, 로그아웃 시 모든 세션을 한번에 종료 가능
        - Redis SCAN 명령어로 패턴 매칭 후 해당 토큰 키들을 일괄 삭제 가능
        """
        await token_redis.setex(f"user_tokens:{user_id}:{jti}", expire, "valid")


    @staticmethod
    async def get_access_token(jti: str) -> Optional[str]:
        """
        Redis에서 액세스 토큰 JTI에 해당하는 user_id 조회
        존재하지 않으면 None 반환
        """
        raw = await token_redis.get(f"access_token:{jti}")
        if raw is None:
            return None
        return raw.decode("utf-8")
    

    @staticmethod
    async def scan_keys(cursor: int, pattern: str, count: int = 100) -> tuple[bytes, list[str]]:
        """Redis SCAN 명령으로 키를 검색"""
        return await token_redis.scan(cursor=cursor, match=pattern, count=count)

    @staticmethod
    async def delete_access_token(jti: str) -> None:
        """Redis에서 액세스 토큰 JTI 키 삭제(토큰 무효화)"""
        await token_redis.delete(f"access_token:{jti}")

    @staticmethod
    async def delete_user_token_key(user_id: str, jti: str) -> None:
        """특정 사용자 토큰 키 삭제"""
        await token_redis.delete(f"user_tokens:{user_id}:{jti}")

    @staticmethod
    async def delete_keys(keys: list[str]) -> None:
        """여러 Redis 키를 한 번에 삭제"""
        if keys:
            await token_redis.delete(*keys)


# client token
class RedisCacheService:
    @staticmethod
    async def cache_user_info(user: User):
        """유저 정보를 Redis에 캐싱(1일 후 만료)"""
        if not user.user_id or not user.email or not user.nickname:
            raise ValueError("Invalid user data for caching")
        
        cache_data = {
            "user_id":user.user_id,
            "email":user.email,
            "nickname":user.nickname,
            "status":user.status.value,
            "role":user.role.value,
        }

        key = f"user_cache:{user.user_id}"
        await client_redis.set(key, json.dumps(cache_data), ex=3600)
    
    @staticmethod
    async def get_cached_user_info(user_id: str):
        """Redis에서 유저 정보 조회"""
        key = f"user_cache:{user_id}"
        data = await client_redis.get(key)
        if data:
            return json.loads(data)
        return None

    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """유저 캐시 무효화(삭제)"""
        await client_redis.delete(f"user_cache:{user_id}")
    """
    캐시에서 삭제 조건(필수)
    1. 사용자 계정 상태가 변경될 때
    2. 사용자 권한이 변경될 때
    3. 사용자 정보가 민감하게 바뀌었을 떄
    """
        

# password_reset_redis
class PasswordResetRedisService:
    def __init__(self):
        self.redis = password_reset_redis
        self.expire_seconds = 600
        self.key_prefix = "password_reset:"

    async def generate_token(self):
        """중복되지 않는 고유한 토큰 생성"""

        # 최대 5회 중복 체크 후 생성 실패 시 예외 발생
        for _ in range(5):
            token = secrets.token_urlsafe(32)
            key = self.key_prefix + token 
            if not await self.redis.exists(key):
                return token 
        raise RuntimeError("토큰 생성 실패")

    async def save_token(self, token: str, email: str, user_id: str):
        """Redis에 토큰과 관련 정보를 JSON 형태로 저장"""
        value = json.dumps({"email": email.lower(), "user_id": user_id})
        # 저장시 지정된 expire_seconds 동안만 유효
        await self.redis.setex(self.key_prefix + token, self.expire_seconds, value)
    
    async def get_token_data(self, token: str):
        """Redis에서 토큰에 해당하는 데이터를 조회"""
        data = await self.redis.get(self.key_prefix + token)
        if data:
            return json.loads(data)
        return None 
    
    async def delete_token(self, token: str):
        """토큰이 사용 완료되었거나 만료 시, Redis에서 해당 키를 삭제하여 무효화"""
        await self.redis.delete(self.key_prefix + token)




"""
async def get_user_from_db(user_id: str) -> Optional[str]:
    # DB에서 사용자 ID로 데이터 직접 조회
    user = await db.get_user(user_id)
    return user.username if user else None

username = await RedisManager.safe_cache_get(f"user:{user_id}:username", get_user_from_db)

[결과]
Redis가 정상일 경우 → Redis에서 읽음
Redis가 죽었거나 key 없음 → get_user_from_db(user_id) 호출해서 DB 조회함

"""

"""
앱 종료시 같이 redis 닫아주기
@app.on_event("shutdown")
async def shutdown_event():
    await client_redis.close()
    await email_redis.close()
    await token_redis.close()

"""