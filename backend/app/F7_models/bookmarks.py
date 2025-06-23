from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Bookmark(Base):
    __tablename__ = 'bookmarks'

    # Primary Key - 북마크의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 북마크한 사용자 ID (외래키, NULL 불가)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # 북마크된 피드 ID (외래키, NULL 불가)
    feed_id = Column(Integer, ForeignKey('feeds.id'), nullable=False)

    # 북마크 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 관계 설정
    user = relationship("User", back_populates="bookmarks")  # 북마크한 사용자 정보
    feed = relationship("Feed", back_populates="bookmarks")  # 북마크된 피드 정보

    # 제약조건 및 인덱스 설정
    __table_args__ = (
        UniqueConstraint('user_id', 'feed_id', name='uq_user_feed_bookmark'),  # 사용자별 피드 중복 북마크 방지
        Index('idx_bookmark_user', 'user_id'),  # 사용자별 북마크 목록 조회를 위한 인덱스
        Index('idx_bookmark_feed', 'feed_id'),  # 피드별 북마크 수 집계를 위한 인덱스
    )
