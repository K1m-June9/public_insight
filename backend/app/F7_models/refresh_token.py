from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
import uuid

from app.F5_core.config import settings
from app.F8_database.connection import Base
# revoked = False : 유효한 토큰
# revoked = True : 사용불가 토큰(무효화된 토큰)
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey('users.user_id', ondelete="CASCADE"),
    nullable=False,
    index=True)
    device_id = Column(String(128), nullable=False)
    token = Column(String(36), unique=True, nullable=False, index=True)
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)  # 무효화 여부
    last_used_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")

    @staticmethod
    def generate_token_expiry(days: int = settings.REFRESH_TOKEN_EXPIRE_DAYS) -> datetime:
        return datetime.utcnow() + timedelta(days=days)

    @staticmethod
    def generate_token() -> str:
        return str(uuid.uuid4())
