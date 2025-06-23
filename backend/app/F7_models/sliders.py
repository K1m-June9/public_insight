from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from app.F8_database.connection import Base

class Slider(Base):
    __tablename__ = 'sliders'

    # Primary Key - 슬라이더의 고유 식별자
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 슬라이더 제목 (최대 500자, NULL 불가)
    title = Column(String(500), nullable=False)

    # 슬라이더 preview(제한 없는 텍스트) - 근데 길게 쓰지 말것
    preview = Column(Text)
    
    #슬라이더 태그(최대 1100자, NULL 불가)
    tag = Column(String(100), nullable=False)

    # 슬라이더 내용/설명 (제한 없는 텍스트)
    content = Column(Text)

    # 슬라이더 작성자명 (최대 100자, NULL 불가)
    author = Column(String(100), nullable=False)

    # 슬라이더 이미지 파일의 저장 경로 (최대 1000자)
    image_path = Column(String(1000))

    # 슬라이더 표시 순서 (기본값: 0, 낮은 숫자가 먼저 표시)
    display_order = Column(Integer, default=0, nullable=False)

    # 슬라이더 활성화 상태 (기본값: True)
    is_active = Column(Boolean, default=True, nullable=False)

    # 슬라이더 노출 시작 일시
    start_date = Column(DateTime)

    # 슬라이더 노출 종료 일시
    end_date = Column(DateTime)

    # 슬라이더 생성 일시 (자동 설정)
    created_at = Column(DateTime, nullable=False, default=func.current_timestamp())

    # 슬라이더 최종 수정 일시 (수정시 자동 업데이트)
    updated_at = Column(DateTime, onupdate=func.current_timestamp())

    # 인덱스 설정
    __table_args__ = (
        Index('idx_slider_display_order', 'display_order'),                    # 표시 순서별 정렬을 위한 인덱스
        Index('idx_slider_active_dates', 'is_active', 'start_date', 'end_date'), # 활성 슬라이더 필터링을 위한 복합 인덱스
    )
