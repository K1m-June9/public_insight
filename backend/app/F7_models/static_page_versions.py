from sqlalchemy import Column, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.F8_database.connection import Base
from datetime import datetime

class StaticPageVersion(Base):
    __tablename__ = "static_page_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("static_pages.id"), nullable=False)
    content = Column(Text, nullable=False)  # 해당 시점의 Markdown 내용
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    page = relationship("StaticPage", back_populates="versions")