from sqlalchemy import Column, Integer, ForeignKey, String, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class WordCloud(Base):
    __tablename__ = 'word_clouds'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    keyword = Column(String(100), nullable=False)   # 키워드 텍스트
    score = Column(Float, nullable=False, default=0.0) # 중요도 점수

    organization = relationship("Organization", back_populates="word_cloud")