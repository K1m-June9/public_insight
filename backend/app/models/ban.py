###___테이블 선언 및 관계 설정하는 파일___###
import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Enum, DateTime, Text, Double, LargeBinary, Numeric, BIGINT, func
from sqlalchemy.sql import text
from sqlalchemy.orm import relationship

# 커스텀 모듈
from app.database.init_db import Base 

# 제재 테이블
class restriction_history(Base):
    __tablename__ = "restriction_history"

    id = Column(Integer, primary_key=True, index=True) # PK
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), nullable=False) # 제약 대상
    type = Column(Enum("suspend", "unsuspend"), nullable=False) # 제약 타입
    reason = Column(String(255), nullable=False) # 제약 사유
    duration = Column(Integer)  # 제약 기간(일 단위), NULL이면 무기한
    suspended_until = Column(DateTime)  # 정지 종료 시각, NULL이면 무기한
    created_by = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL")) # 제약 조치를 취한 관리자 ID
    created_at = Column(DateTime, default=func.now()) # 레코드 생성 시각

    # Relationships
    user = relationship("user_table", foreign_keys=[user_id], back_populates="restrictions") # 제약 대상 사용자
    admin = relationship("user_table", foreign_keys=[created_by]) # 제약 조치를 취한 관리자


# 금칙어 단어 테이블
class banned_keywords(Base):
    __tablename__ = "banned_keywords"
    banned_keywords_id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)  # 금칙어 고유 ID (PK)
    keyword = Column(String(50), unique=True, nullable=False)  # 금칙어