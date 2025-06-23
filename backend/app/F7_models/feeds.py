from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Feed(Base):
    __tablename__ = 'feeds'

    # Primary Key - 피드의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 소속 기관 ID (외래키, NULL 불가)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)

    # 소속 카테고리 ID (외래키, NULL 불가)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    # 피드 제목 (최대 500자, NULL 불가)
    title = Column(String(500), nullable=False)

    # NLP로 생성된 요약문 (제한 없는 텍스트)
    summary = Column(Text)

    # 원본 텍스트 내용 (제한 없는 텍스트)
    original_text = Column(Text)

    # PDF 파일의 파일 시스템 저장 경로 (최대 1000자)
    pdf_file_path = Column(String(1000))

    # 원본 콘텐츠의 URL 주소 (최대 1000자)
    source_url = Column(String(1000))

    # 원본 콘텐츠의 발행 일시
    published_date = Column(DateTime)

    # 피드 활성화 상태 (기본값: True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 피드 조회수 (기본값: 0)
    view_count = Column(Integer, default=0, nullable=False)

    # 피드 등록 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 피드 정보 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 관계 설정
    organization = relationship("Organization", back_populates="feeds")  # 소속 기관 정보
    category = relationship("Category", back_populates="feeds")  # 소속 카테고리 정보
    bookmarks = relationship("Bookmark", back_populates="feed", cascade="all, delete-orphan")  # 피드의 북마크 목록
    ratings = relationship("Rating", back_populates="feed", cascade="all, delete-orphan")  # 피드의 평점 목록

    # 인덱스 설정
    __table_args__ = (
        Index('idx_feed_organization', 'organization_id'),    # 기관별 피드 검색을 위한 인덱스
        Index('idx_feed_category', 'category_id'),           # 카테고리별 피드 검색을 위한 인덱스
        Index('idx_feed_created_at', 'created_at'),          # 등록일순 정렬을 위한 인덱스
        Index('idx_feed_published_date', 'published_date'),  # 발행일순 정렬을 위한 인덱스
    )
