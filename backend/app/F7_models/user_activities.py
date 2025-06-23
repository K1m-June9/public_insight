from sqlalchemy import Column, Integer, String, DateTime,  ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class UserActivity(Base):
    __tablename__ = 'user_activities'

    # Primary Key - 사용자 활동의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 활동한 사용자 ID (외래키, 비로그인 사용자는 NULL)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    # 활동 유형 (LOGIN/FEED_VIEW/SEARCH/BOOKMARK/RATING 등, 최대 50자)
    activity_type = Column(String(50), nullable=False)

    # 활동 대상 ID (feed_id, search_log_id 등 활동에 따라 다름)
    target_id = Column(Integer)

    # 사용자의 IP 주소 (IPv6 지원을 위해 최대 45자)
    ip_address = Column(String(45))

    # 사용자의 브라우저 정보 (User-Agent, 제한 없는 텍스트)
    user_agent = Column(Text)

    # 활동 발생 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 관계 설정
    user = relationship("User", back_populates="user_activities")  # 활동한 사용자 정보 (비로그인시 NULL)

    # 인덱스 설정
    __table_args__ = (
        Index('idx_user_activity_user', 'user_id'),           # 사용자별 활동 기록 조회를 위한 인덱스
        Index('idx_user_activity_type', 'activity_type'),     # 활동 유형별 통계를 위한 인덱스
        Index('idx_user_activity_created_at', 'created_at'),  # 시간별 활동 통계를 위한 인덱스
    )
