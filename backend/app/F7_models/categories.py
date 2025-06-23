from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Category(Base):
    __tablename__ = 'categories'

    # Primary Key - 카테고리의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 소속 기관 ID (외래키, NULL 불가)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)

    # 카테고리명 (최대 100자, NULL 불가)
    name = Column(String(100), nullable=False)

    # 카테고리 설명 (제한 없는 텍스트)
    description = Column(Text)

    # 카테고리 활성화 상태 (기본값: True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 카테고리 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 카테고리 정보 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 관계 설정
    organization = relationship("Organization", back_populates="categories")  # 소속 기관 정보
    feeds = relationship("Feed", back_populates="category")  # 카테고리의 피드 목록

    # 제약조건 및 인덱스 설정
    __table_args__ = (
        UniqueConstraint('organization_id', 'name', name='uq_organization_category'),  # 기관 내 카테고리명 중복 방지
        Index('idx_category_organization', 'organization_id'),  # 기관별 카테고리 검색을 위한 인덱스
    )
