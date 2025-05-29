###___테이블 선언 및 관계 설정하는 파일___###
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, DateTime, Text, Double, LargeBinary, Numeric, BIGINT, func
import uuid

from sqlalchemy.sql import text
from sqlalchemy.orm import relationship

# 커스텀 모듈
from app.database.init_db import Base 

# 사용자 디바이스 정보 테이블(다중 디바이스를 위한)
class device_info(Base):
    __tablename__ = "device_info"
    device_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False) # 디바이스 고유 ID(PK)
    username = Column(String(50), ForeignKey('user_table.username'), nullable=False)  # ID (FK)
    device_name = Column(String(255), nullable=False) # 디바이스 이름
    last_login = Column(DateTime, server_default=func.now(), onupdate=func.now()) # 마지막 로그인 시간(추후 확장할 수 있는 부분)

    user = relationship("user_table", back_populates="devices")  # 사용자와의 관계 설정
    refresh_tokens = relationship("refresh_tokens", back_populates="device", cascade="all, delete-orphan")  # Refresh Token 관계 설정


# Refresh Token 테이블
class refresh_tokens(Base):
    __tablename__ = "refresh_tokens"
    refresh_token_id = Column(BIGINT, primary_key=True, index=True, autoincrement=True) # 토큰 고유 ID
    device_id = Column(String(36), ForeignKey('device_info.device_id'), unique=True, nullable=False) # 디바이스 ID
    refresh_token = Column(String(255), nullable=False) # Refresh Token 값
    expires_at = Column(DateTime, nullable=False)

    device = relationship("device_info", back_populates="refresh_tokens")

