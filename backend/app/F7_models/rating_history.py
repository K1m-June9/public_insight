from sqlalchemy import Column, Integer, String, DateTime,  ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class RatingHistory(Base):
    __tablename__ = 'rating_history'

    # Primary Key - 평점 이력의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 대상 평점 ID (외래키, NULL 불가)
    rating_id = Column(Integer, ForeignKey('ratings.id'), nullable=False)

    # 변경 전 점수 (삭제시에는 NULL)
    old_score = Column(Integer)

    # 변경 후 점수 (생성시 이전값은 NULL)
    new_score = Column(Integer)

    # 수행된 작업 유형 (CREATE/UPDATE/DELETE, 최대 20자)
    action = Column(String(20), nullable=False)

    # 이력 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 관계 설정
    rating = relationship("Rating", back_populates="rating_history")  # 대상 평점 정보

    # 인덱스 설정
    __table_args__ = (
        Index('idx_rating_history_rating', 'rating_id'),      # 평점별 이력 조회를 위한 인덱스
        Index('idx_rating_history_created_at', 'created_at'), # 시간순 이력 조회를 위한 인덱스
    )
