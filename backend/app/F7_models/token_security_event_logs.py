### 임시 ###
from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.F8_database.connection import Base

class TokenSecurityEventLog(Base):
    __tablename__ = "token_security_event_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_metadata = Column(JSON) 
    created_at = Column(DateTime, default=datetime.utcnow)
