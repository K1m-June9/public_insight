from fastapi import Request, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from redis.exceptions import RedisError
from pydantic_settings import BaseSettings
from datetime import timedelta
import logging
from typing import Optional, Dict, Any, Callable, Awaitable

from app.F7_models.users import User



from app.F5_core.config import settings
logger = logging.getLogger(__name__)

# Redis 접속 URL을 환경변수로 관리하는 설정 클래스
class RedisSettings(BaseSettings):
    ENVIRONMENT: str = "development"    # 기본값 dev
    IS_LOCAL: bool = True               # 로컬 실행 여부 플래그

    CLIENT_REDIS_URL: Optional[str] = None
    EMAIL_REDIS_URL: Optional[str] = None
    TOKEN_REDIS_URL: Optional[str] = None

    def __init__(self, **values):
        super().__init__(**values)

        # 프로덕션 환경이라면 로컬이 아닐 경우 Redis 서버 주소 다르게 설정
        if self.ENVIRONMENT == "production" and not self.IS_LOCAL:
            base = "redis://redis_server:6379"
        else:  # dev or local test
            base = "redis://localhost:6379"

        # 각 Redis 용도별 URL을 기본값으로 세팅 (설정값이 있으면 덮어씀)
        self.CLIENT_REDIS_URL = self.CLIENT_REDIS_URL or f"{base}/0"
        self.EMAIL_REDIS_URL = self.EMAIL_REDIS_URL or f"{base}/1"
        self.TOKEN_REDIS_URL = self.TOKEN_REDIS_URL or f"{base}/13"

    model_config = {
        "env_file": ".env",                 # 환경변수 파일 경로
        "env_file_encoding": "utf-8",       # 인코딩
        "extra": "ignore",                  # 추가 환경변수 무시
    }

# 환경변수 기반 Redis 설정 인스턴스 생성
redis_settings = RedisSettings()

# Redis 클라이언트 인스턴스 생성
# 각기 다른 DB 번호 또는 Redis 서버로 분리 운영 가능
client_redis = Redis.from_url(redis_settings.CLIENT_REDIS_URL)  # 일반 캐시용
email_redis = Redis.from_url(redis_settings.EMAIL_REDIS_URL)    # 이메일 처리용
token_redis = Redis.from_url(redis_settings.TOKEN_REDIS_URL)    # 토큰 관리용

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

    @staticmethod
    async def cache_user_data(user_id: str, user_data: Dict[str, Any], expire: int = settings.USER_CACHE_EXPIRE_SECONDS) -> None:
        """
        사용자 정보를 Redis 해시(Hash)로 저장
        - key: user:{user_id}
        - user_data 딕셔너리의 각 키-값을 Redis 해시의 필드-값으로 저장 (값은 모두 문자열로 변환하여 저장)
        - expire: TTL 기본값 1일 (기본 1일, 86400초)

        Args:
        user_id (str): 사용자 고유 ID
        user_data (Dict[str, Any]): 저장할 사용자 데이터 (필드-값 쌍)
        expire (int, optional): 키 만료 시간(초 단위). 기본값은 설정값 USER_CACHE_EXPIRE_SECONDS
        """
        key = f"user:{user_id}" # Redis에 저장할 키 생성
        args = []
        for k, v in user_data.items():
            args.extend([k, str(v)]) # 값은 반드시 문자열로 변환

        # Redis에 해시 필드-값들을 한 번에 저장
        await client_redis.hset(key, *args)
        # Redis 키에 만료시간(TTL) 설정
        await client_redis.expire(key, expire)


    @staticmethod
    async def get_user_data(user_id: str) -> Dict[str, Any]:
        """
        Redis에서 사용자 정보 해시를 조회하여 반환
        데이터가 없으면 빈 dict 또는 None 반환 예상
        """
        raw_data = await client_redis.hgetall(f"user:{user_id}")
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in raw_data.items()}


    @staticmethod
    async def invalidate_user_cache(user_id: str) -> None:
        """
        사용자 캐시 무효화(삭제)
        - 주로 회원정보 수정 후 사용
        """
        await client_redis.delete(f"user:{user_id}")


    @staticmethod
    async def safe_cache_get(key: str, db_fallback: Callable[[str], Awaitable[Any]]) -> Any:
        """
        Redis 장애를 대비한 안전한 get 메서드
        - 장애 시 DB 조회 함수를 호출해 fallback 처리
        - 예: key를 Redis에서 못찾으면 db_fallback(key)를 실행

        Args:
            key (str): 조회할 Redis 키
            db_fallback (Callable): fallback 비동기 함수

        """
        try:
            val = await client_redis.get(key)
            if val is None:
                return None
            return val.decode("utf-8")
        except RedisError as e:
            logger.warning(f"Redis 장애 발생 ({e}). DB 폴백 실행")
            return await db_fallback(key)

class RedisCacheService:
    @staticmethod
    async def cache_user_info(user: User):
        """유저 정보를 Redis에 캐싱(1일 후 만료)"""
        user_data = {
            "user_id": user.user_id, 
            "role": user.role.value,
            "status": user.status.value,
        }
        key = f"user:{user.user_id}"
        await client_redis.hset(key, mapping=user_data)
        await client_redis.expire(key, timedelta(days=1))
    
    @staticmethod
    async def get_cached_user_info(user_id: str):
        """Redis에서 유저 정보 조회"""
        key = f"user:{user_id}"
        data = await client_redis.hgetall(key)

        # Redis hgetall 결과가 bytes형 dict라면 decode 처리 필요
        if data:
            return {k.decode(): v.decode() for k, v in data.items()}
        return None

    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """유저 캐시 무효화(삭제)"""
        await client_redis.delete(f"user:{user_id}")
    """
    캐시에서 삭제 조건(필수)
    1. 사용자 계정 상태가 변경될 때
    2. 사용자 권한이 변경될 때
    3. 사용자 정보가 민감하게 바뀌었을 떄
    """
        

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