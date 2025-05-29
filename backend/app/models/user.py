###___테이블 선언 및 관계 설정하는 파일___###
from sqlalchemy import Column, String, ForeignKey, Boolean, DateTime, BIGINT, Integer, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
# 커스텀 모듈
from app.database.init_db import Base 

class user_role(PyEnum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class user_status(PyEnum):
    active = "active"
    inactive = "inactive"
    suspended = "suspended"


# 사용자 개인정보 테이블
class user_table(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True, index=True) # 고유 ID (PK)
    username = Column(String(50), unique=True, nullable=False, index=True)  # 회원 ID 
    nickname = Column(String(40), unique=True, nullable=False) # 닉네임
    password_hash = Column(String(255), nullable=False) # 비밀번호 해시 
    email = Column(String(255), unique=True, nullable=False, index=True) # 이메일

    advertising_consent = Column(Boolean, nullable=False) # 광고 동의 여부
    notification = Column(Boolean, nullable=False) # 알림 허용 여부
    terms_agreed = Column(Boolean, nullable=False, default=True) # 약관 동의 여부
    
    role = Column(SQLEnum(user_role), nullable=False, default=user_role.user) # 유저 권한
    status = Column(SQLEnum(user_status), nullable=False, default=user_status.active) # 유저 상태

    suspended_until = Column(DateTime) # 제재기간
    created_at = Column(DateTime, default=func.now()) # 가입일자
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) # 수정일자

    restrictions = relationship("restriction_history", foreign_keys="restriction_history.user_id", back_populates="user")
    devices = relationship("device_info", back_populates="user", cascade="all, delete-orphan")  # 다중 디바이스를 위한 관계 설정

    
    #notifications = relationship("notification", back_populates="user", cascade="all, delete-orphan")
