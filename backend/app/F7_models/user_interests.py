from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class UserInterest(Base):
    __tablename__ = 'user_interests'
    
    # Primary Key - 사용자 관심사의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 사용자 ID (외래키, NULL 불가)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 관심 기관 ID (외래키, NULL 불가)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # 관심사 등록 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    # 관계 설정
    user = relationship("User")
    organization = relationship("Organization")
    
    # 제약조건 및 인덱스
    __table_args__ = (
        UniqueConstraint('user_id', 'organization_id', name='uq_user_organization_interest'),
        Index('idx_user_interest_user', 'user_id'),
    )