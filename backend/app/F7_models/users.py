from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.F8_database.connection import Base

    # 사용자 역할을 정의하는 Enum
class UserRole(enum.Enum):
    USER = "user"          # 일반 사용자
    MODERATOR = "moderator"  # 중재자
    ADMIN = "admin"        # 관리자

# 사용자 계정 상태를 정의하는 Enum
class UserStatus(enum.Enum):
    ACTIVE = "active"        # 활성 상태
    INACTIVE = "inactive"    # 비활성 상태
    SUSPENDED = "suspended"  # 정지 상태
    DELETED = "deleted"      # 삭제 상태

class User(Base):
    __tablename__ = 'users'

    # Primary Key - 시스템 내부에서 사용하는 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 사용자가 로그인시 사용하는 아이디 (중복 불가, 최대 50자)
    user_id = Column(String(50), unique=True, nullable=False, index=True)

    # 사용자 이메일 주소 (중복 불가, 최대 255자)
    email = Column(String(255), unique=True, nullable=False, index=True)

    # 암호화된 비밀번호 해시값 (최대 255자)
    password_hash = Column(String(255), nullable=False)

    # 사용자 닉네임 (중복 불가, 최대 50자)
    nickname = Column(String(50), unique=True, nullable=False, index=True)

    # 사용자 역할 (USER/MODERATOR/ADMIN, 기본값: USER)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # 계정 상태 (ACTIVE/INACTIVE/SUSPENDED/DELETED, 기본값: ACTIVE)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    # 이용약관 동의 여부 (기본값: False)
    terms_agreed = Column(Boolean, default=False, nullable=False)

    # 개인정보처리방침 동의 여부 (기본값: False)
    privacy_agreed = Column(Boolean, default=False, nullable=False)

    # 알림 정보 수신 동의 여부 (기본값: False)
    notification_agreed = Column(Boolean, default=False, nullable=False)

    # 이용약관 동의 일시 (법적 요구사항을 위한 기록)
    terms_agreed_at = Column(DateTime)

    # 개인정보처리방침 동의 일시 (법적 요구사항을 위한 기록)
    privacy_agreed_at = Column(DateTime)

    # 마케팅 정보 수신 동의 일시 (법적 요구사항을 위한 기록)
    marketing_agreed_at = Column(DateTime)

    # 계정 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 계정 정보 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 관계 설정
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")  # 사용자의 북마크 목록
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")      # 사용자의 평점 목록
    search_logs = relationship("SearchLog", back_populates="user", cascade="all, delete-orphan")  # 사용자의 검색 기록
    user_activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")  # 사용자의 활동 기록

    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan", passive_deletes=True) # 사용자의 refresh token
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_user_role', 'role'),              # 역할별 검색을 위한 인덱스
        Index('idx_user_status', 'status'),          # 상태별 검색을 위한 인덱스
        Index('idx_user_created_at', 'created_at'),  # 가입일순 정렬을 위한 인덱스
    )