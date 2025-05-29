import os
from pydantic_settings import BaseSettings
from redis.asyncio import Redis

class Settings(BaseSettings):
    # JWT 설정
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # 데이터베이스 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

    # 이메일(SMTP) 설정
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL: str
    EMAIL_PASSWORD: str

    # 기본 Redis (로그인, 세션 등)
    REDIS_URL: str = "redis://redis_server:6379/0"

    # 이메일 인증 전용 Redis
    EMAIL_REDIS_URL: str = "redis://redis_server:6379/1"

    # 디버그 모드
    DEBUG: bool  

    # 환경 구분 설정
    # 개발 환경 여부 (True면 개발용 환경)
    IS_LOCAL: bool = os.getenv("IS_LOCAL", "False").lower() == "True"

    # secure cookie 여부(개발 환경에서는 False로 설정)
    SECURE_COOKIE: bool = not IS_LOCAL

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {
        "extra": "allow",  # .env 파일의 추가 필드 허용
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# 설정 객체 생성
settings = Settings()

# Redis 클라이언트 객체 생성
# 로그인, 세션, 토큰 관리
login_redis = Redis.from_url(settings.REDIS_URL)

# 이메일 인증 전용
email_redis = Redis.from_url(settings.EMAIL_REDIS_URL)