from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # JWT 설정
    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    USER_CACHE_EXPIRE_SECONDS: int

    # 암호화 키
    ENCRYPTION_KEY: str

    # DB 설정
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # SMTP 설정
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL: str
    EMAIL_PASSWORD: str

    # 환경 설정
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: Optional[str] = None
    DEBUG: bool
    IS_LOCAL: bool = False

    @property
    def SECURE_COOKIE(self) -> bool:
        return not self.IS_LOCAL

    @property
    def DATABASE_URL(self) -> str:
        """
        DATABASE 접속 URL을 환경에 따라 동적으로 반환합니다.
        1. 개발환경 + 로컬 실행 (localhost)
        2. 개발환경 + 도커 실행 (DB는 docker-compose의 서비스명으로 접근)
        3. 운영환경 (실제 운영 DB 주소)
        """
        if self.ENVIRONMENT == "development":
            if self.IS_LOCAL:
                # 예: 로컬에서 실행하는 경우
                return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@localhost:{self.DB_PORT}/{self.DB_NAME}"
            else:
                # 도커 환경에서 개발 실행 (예: 도커 컴포즈에서 'db'라는 서비스명으로 DB 접속)
                return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else:
            # 운영 환경 
            return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    model_config = {
        "extra": "allow",  # 앱 전체 환경 변수는 자유롭게 허용
        "env_file": "../.env",
        "env_file_encoding": "utf-8",
    }

settings = Settings()
