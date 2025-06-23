from sqlalchemy import Column, Integer, DateTime,  ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Rating(Base):
    __tablename__ = 'ratings'

    # Primary Key - 평점의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 평점을 남긴 사용자 ID (외래키, NULL 불가)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # 평점이 매겨진 피드 ID (외래키, NULL 불가)
    feed_id = Column(Integer, ForeignKey('feeds.id'), nullable=False)

    # 평점 점수 (1-5점, NULL 불가)
    score = Column(Integer, nullable=False)

    # 평점 최초 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 평점 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 관계 설정
    user = relationship("User", back_populates="ratings")  # 평점을 남긴 사용자 정보
    feed = relationship("Feed", back_populates="ratings")  # 평점이 매겨진 피드 정보
    rating_history = relationship("RatingHistory", back_populates="rating", cascade="all, delete-orphan")  # 평점 변경 이력

    # 제약조건 및 인덱스 설정
    __table_args__ = (
        UniqueConstraint('user_id', 'feed_id', name='uq_user_feed_rating'),  # 사용자별 피드 중복 평점 방지
        Index('idx_rating_user_feed', 'user_id', 'feed_id'),  # 사용자-피드 조합 검색을 위한 복합 인덱스
    )
