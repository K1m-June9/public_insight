from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Organization(Base):
    __tablename__ = 'organizations'

    # Primary Key - 기관의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 기관명 (중복 불가, 최대 200자)
    name = Column(String(200), unique=True, nullable=False)

    # 기관 설명 (제한 없는 텍스트)
    description = Column(Text)

    # 기관 웹사이트 URL (최대 500자)
    website_url = Column(String(500))
    
    # 기관 이미지 파일의 저장 경로 (최대 1000자)
    icon_path = Column(String(1000))

    # 기관 활성화 상태 (기본값: True -> False로 변경)
    is_active = Column(Boolean, default=False, nullable=False)

    # 기관 등록 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 기관 정보 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 관계 설정
    categories = relationship("Category", back_populates="organization", cascade="all, delete-orphan")  # 기관의 카테고리 목록
    feeds = relationship("Feed", back_populates="organization")  # 기관의 피드 목록
    keywords = relationship("Keyword", back_populates="organization", cascade="all, delete-orphan") # 키워드 연결
    word_cloud = relationship("WordCloud", back_populates="organization", uselist=False, cascade="all, delete-orphan") #기관별 워드 클라우드 목록
