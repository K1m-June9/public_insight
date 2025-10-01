"""
구글 코랩 런타임이 끊길 때마다 nlp_server_url이 바뀌는 문제가 있음
이를 해결하기 위해 .env를 매일 수정하는 대신,
데이터베이스에 nlp_server_url만 저장하고 관리자 모드에서만 수정할 수 있도록 제한

보안상 위험을 줄이기 위해 nlp_server_url 외 다른 설정값은 DB에 저장하지 않을 것
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from app.F8_database.connection import Base


class AppSettings(Base):
    __tablename__ = 'app_settings'
    id = Column(Integer, primary_key=True, index=True)
    key_name = Column(String(255), unique=True, index=False)
    key_value = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

