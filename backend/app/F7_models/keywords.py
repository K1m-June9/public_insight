from sqlalchemy import Column, Integer, String, DateTime,  ForeignKey, UniqueConstraint, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Keyword(Base):
    __tablename__ = 'keywords'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기관 ID (외래키)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # 키워드 텍스트 (최대 100자)
    keyword_text = Column(String(100), nullable=False)
    
    # 누적 점수 (KeyBERT 점수 + 빈도 가중치)
    total_score = Column(Float, default=0.0, nullable=False)
    
    # 출현 횟수 (빈도)
    frequency = Column(Integer, default=1, nullable=False)
    
    # 최초 생성일
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    # 최종 업데이트일 (점수 누적시 갱신)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # 관계 설정
    organization = relationship("Organization", back_populates="keywords")
    
    # 인덱스 및 제약조건
    __table_args__ = (
        Index('idx_keyword_org_text', 'organization_id', 'keyword_text'),
        UniqueConstraint('organization_id', 'keyword_text', name='uq_org_keyword'),
    )