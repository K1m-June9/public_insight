import logging
import secrets
import json
import os

from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from redis.exceptions import RedisError
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from datetime import timedelta, datetime 
from typing import Optional, Dict, Any, Callable, Awaitable, List 

from app.F5_core.config import settings
from app.F6_schemas.base import BaseResponse
from app.F6_schemas.admin.crawl_task_redis import (
    TaskStatus, 
    JobName, 
    CrawlTaskResult, 
    CrawlTaskResponse, 
    CrawlTaskData,
    CrawlAllTaskResponse,

    )
from app.F7_models.users import User




logger = logging.getLogger(__name__)


# =================================================
# Redis 설정 클래스 (환경변수 + URL 자동 생성)
# =================================================
class RedisSettings(BaseSettings):
    ENVIRONMENT: str = "development"
    IS_LOCAL: bool = True

    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None

    CLIENT_REDIS_URL: Optional[str] = None
    EMAIL_REDIS_URL: Optional[str] = None
    TOKEN_REDIS_URL: Optional[str] = None
    PASSWORD_RESET_REDIS_URL: Optional[str] = None
    CRAWL_TASK_REDIS_URL: Optional[str] = None

    model_config = ConfigDict(
        env_file =  os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env")),
        env_file_encoding = "utf-8",
        extra = "ignore",
    )

    # 기본 Redis URL 생성(환경별 host, port 적용)
    def _default_base_url(self) -> str:
        host = self.REDIS_HOST or ("redis_server" if self.ENVIRONMENT == "production" and not self.IS_LOCAL else "localhost")
        port = self.REDIS_PORT or 6379
        return f"redis://{host}:{port}"


    # 클라이언트 캐시용 Redis URL
    def get_client_url(self) -> str:
        return self.CLIENT_REDIS_URL or f"{self._default_base_url()}/0"

    # 이메일 인증 코드 Redis URL
    def get_email_url(self) -> str:
        return self.EMAIL_REDIS_URL or f"{self._default_base_url()}/1"
    
    # 백그라운드 작업 크롤링용 Redis URL
    def get_crawl_task_url(self) -> str:
        return self.CRAWL_TASK_REDIS_URL or f"{self._default_base_url()}/2"

    # 토큰 관리용 Redis URL
    def get_token_url(self) -> str:
        return self.TOKEN_REDIS_URL or f"{self._default_base_url()}/13"
    
    # 비밀번호 재설정용 Redis URL
    def get_password_reset_url(self) -> str:
        return self.PASSWORD_RESET_REDIS_URL or f"{self._default_base_url()}/14"
    

# =================================================
# Redis 인스턴스 생성
# =================================================
redis_settings = RedisSettings()

client_redis = Redis.from_url(redis_settings.get_client_url())
email_redis = Redis.from_url(redis_settings.get_email_url())
token_redis = Redis.from_url(redis_settings.get_token_url())
password_reset_redis = Redis.from_url(redis_settings.get_password_reset_url())
crawl_task_redis = Redis.from_url(redis_settings.get_crawl_task_url())



# =================================================
# RedisManager - 액세스 토큰 및 세션 관리
# =================================================
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
        존재하지 않으면 None 반환 -> 무효화된 토큰으로 간주
        """
        raw = await token_redis.get(f"access_token:{jti}")
        if raw is None:
            return None
        return raw.decode("utf-8")
    

    @staticmethod
    async def scan_keys(cursor: int, pattern: str, count: int = 100) -> tuple[bytes, list[str]]:
        """SCAN 명령으로 특정 패턴의 Redis 키 검색"""
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


# =================================================
# RedisCacheService - 사용자 정보 캐싱
# =================================================
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
        

# =================================================
# PasswordResetRedisService - 비밀번호 재설정 토큰 관리
# =================================================
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


# =================================================
# CrawlTaskRedisService - 크롤링 작업(Task) 상태 및 큐 관리 서비스
# =================================================
class CrawlTaskRedisService:
    def __init__(self):
        self.redis = crawl_task_redis
        self.status_prefix = "crawl_tasks:status"
        self.ttl_seconds= 12 * 3600
        
    # -----------------------------
    # 1. 작업 생성 (PENDING 상태)
    # -----------------------------
    async def add_task(
            self, 
            task_id: str, 
            job_name: JobName,
    ) -> str:
        """
        Redis에 새로운 크롤링 작업을 JSON 형태로 기록
        """
        key = f"{self.status_prefix}{task_id}"
        value = {
            "job": job_name,
            "status": TaskStatus.PENDING.value,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "target_orgs": [],
            "total_items": 0, 
            "message": None 
        }

        await self.redis.set(key, json.dumps(value, ensure_ascii=False), ex=self.ttl_seconds)
        return task_id 
    
    # -----------------------------
    # 2. 작업 상태 갱신
    # -----------------------------
    async def update_task_status(
            self, 
            task_id: str, 
            status: TaskStatus, 
            result: Optional[CrawlTaskResult] = None
    ):
        """
        Redis에 특정 작업 ID의 상태를 갱신
        """
        key = f"{self.status_prefix}{task_id}"
        status_data_raw = await self.redis.get(key)

        if status_data_raw:
            data = json.loads(status_data_raw.decode("utf-8"))
        else: 
            data = {
                "job": result.job_name if result else None,
                "status": status.value,
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": None,
                "target_orgs": [],
                "total_items": 0, 
                "message": None 
            }
    
        data["status"] = status.value 
        if status == TaskStatus.COMPLETED: 
            data["completed_at"] = datetime.utcnow().isoformat()
        if status == TaskStatus.FAILED: 
            data["message"] = result.message if result and result.message else "Unknown error" 
        

        if result: 
            data.update(result.model_dump(exclude_none=True, exclude={"status"}))

        await self.redis.set(key, json.dumps(data, ensure_ascii=False), ex=self.ttl_seconds)
        logger.debug(f"Task {task_id} status updated to: {status.value}")

    # -----------------------------
    # 3. 작업 상태 조회
    # -----------------------------
    async def get_task_info(self, task_id: str) -> CrawlTaskResponse | BaseResponse:
        """
        특정 작업의 전체 상태 및 메타데이터 조회
        """
        key = f"{self.status_prefix}{task_id}"
        status_bytes = await self.redis.get(key)
        if not status_bytes:
            return BaseResponse(
                success=False
            )
        
        status_data = json.loads(status_bytes.decode("utf-8"))

        task_data = CrawlTaskData(
            task_id=task_id,
            job_name=status_data.get("job", ""),
            status=status_data.get("status"),
            started_at=datetime.fromisoformat(status_data.get("started_at")),
            completed_at=datetime.fromisoformat(status_data["completed_at"]) if status_data.get("completed_at") else None,
            target_orgs=status_data.get("target_orgs", []),
            total_items=status_data.get("total_items", 0),
            message=status_data.get("message")
        )

        return CrawlTaskResponse(
            success=True, 
            data=task_data
        )
    
    # -----------------------------
    # 4. 전체 작업 상태 조회
    # -----------------------------
    async def get_all_task_info(self) -> CrawlAllTaskResponse:
        """
        Redis에 등록된 모든 작업의 전체 정보 조회
        반환: {task_id}: {..작업 정보 ..}
        """
        keys = await self.redis.keys(f"{self.status_prefix}*")
        all_tasks = []

        for key in keys:  
            task_id = key.decode("utf-8").replace(self.status_prefix, "")
            data_bytes = await self.redis.get(key)
            if not data_bytes: 
                continue 
            
            status_data = json.loads(data_bytes.decode("utf-8"))

            all_tasks.append(
                CrawlTaskData(
                    task_id=task_id,
                    job_name=status_data.get("job", ""),
                    status=status_data.get("status"),
                    started_at=datetime.fromisoformat(status_data.get("started_at")),
                    completed_at=datetime.fromisoformat(status_data["completed_at"]) if status_data.get("completed_at") else None,
                    target_orgs=status_data.get("target_orgs", []),
                    total_items=status_data.get("total_items", 0),
                    message=status_data.get("message")
                )
            )
        return CrawlAllTaskResponse(
            success=True,
            data=all_tasks
        )

    # -----------------------------
    # 5. 전체 작업 삭제
    # -----------------------------
    async def delete_all_except_in_progress(self) -> BaseResponse:
        """
        IN_PROGRESS 상태를 제외하고 모든 태스크 삭제
        """
        keys = await self.redis.keys(f"{self.status_prefix}*")
        if not keys: 
            return BaseResponse(
                success=True
            )
        
        for key in keys: 
            status_bytes = await self.redis.get(key)
            if not status_bytes:
                continue 

            status_data = json.loads(status_bytes.decode("utf-8"))
            if status_data.get("status") != TaskStatus.IN_PROGRESS.value: 
                await self.redis.delete(key)
                logger.info(
                    f"Task {key.decode() if isinstance(key, bytes) else key} deleted "
                    f"(status={status_data.get('status')})"
                )
        
        return BaseResponse(
            success=True
        )
        



# =================================================
# 참고 예시: 안전한 캐시 조회
# =================================================
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