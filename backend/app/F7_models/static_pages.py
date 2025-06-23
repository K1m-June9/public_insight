from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.F8_database.connection import Base
from datetime import datetime

class StaticPage(Base):
    __tablename__ = "static_pages"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)  # about, terms, privacy, youth-protection
    #path = Column(String(100), nullable=False)  # /about, /terms, /privacy, /youth-protection
    content = Column(Text, nullable=False)  # Markdown 형태
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계
    versions = relationship("StaticPageVersion", back_populates="page", cascade="all, delete-orphan")