from sqlalchemy import Column, Integer, String, DateTime,  ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class SearchLog(Base):
    __tablename__ = 'search_logs'

    # Primary Key - 검색 로그의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 검색한 사용자 ID (외래키, 비로그인 사용자는 NULL)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # 검색 키워드 (최대 500자, NULL 불가)
    keyword = Column(String(500), nullable=False)

    # 검색 결과 개수 (기본값: 0)
    results_count = Column(Integer, default=0, nullable=False)

    # 검색 수행 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 관계 설정
    user = relationship("User", back_populates="search_logs")  # 검색한 사용자 정보 (비로그인시 NULL)

    # 인덱스 설정
    __table_args__ = (
        Index('idx_search_log_keyword', 'keyword'),        # 키워드별 검색 통계를 위한 인덱스
        Index('idx_search_log_user', 'user_id'),          # 사용자별 검색 기록 조회를 위한 인덱스
        Index('idx_search_log_created_at', 'created_at'), # 시간별 검색 통계를 위한 인덱스
    )
