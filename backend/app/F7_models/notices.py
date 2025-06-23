from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Notice(Base):
    __tablename__ = 'notices'

    # Primary Key - 공지사항의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 공지사항 제목 (최대 500자, NULL 불가)
    title = Column(String(500), nullable=False)

    # 공지사항 내용 (제한 없는 텍스트, NULL 불가)
    content = Column(Text, nullable=False)

    # 공지사항 작성자명 (최대 100자, NULL 불가)
    author = Column(String(100), nullable=False)

    # 상단 고정 여부 (기본값: False)
    is_pinned = Column(Boolean, default=False, nullable=False)

    # 공지사항 활성화 상태 (기본값: True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 공지사항 조회수 (기본값: 0)
    view_count = Column(Integer, default=0, nullable=False)

    # 공지사항 작성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 공지사항 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 인덱스 설정
    __table_args__ = (
        Index('idx_notice_created_at', 'created_at'),  # 작성일순 정렬을 위한 인덱스
        Index('idx_notice_pinned', 'is_pinned'),       # 고정 공지사항 필터링을 위한 인덱스
    )
