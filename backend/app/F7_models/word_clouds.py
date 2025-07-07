from sqlalchemy import Column, Integer, DateTime, ForeignKey, Index, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class WordCloud(Base):
    __tablename__ = 'word_clouds'
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 기관 ID (외래키)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # 워드클라우드 데이터 (JSON 형태로 저장)
    # 예: [{"text": "예산", "value": 85.5}, {"text": "법안", "value": 72.3}, ...]
    cloud_data = Column(JSON, nullable=False)
    
    # 데이터 기준 기간 시작일
    period_start = Column(Date, nullable=False)
    
    # 데이터 기준 기간 종료일  
    period_end = Column(Date, nullable=False)
    
    # 캐시 생성일
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())
    
    # 캐시 업데이트일
    updated_at = Column(DateTime, onupdate=func.current_timestamp())
    
    # 관계 설정
    organization = relationship("Organization", back_populates="word_cloud")
    
    # 인덱스
    __table_args__ = (
        Index('idx_wordcloud_org', 'organization_id'),
        Index('idx_wordcloud_updated', 'updated_at'),
    )