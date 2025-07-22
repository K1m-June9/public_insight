from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict
from datetime import datetime

from app.F6_schemas import base
from app.F7_models.users import UserRole, UserStatus

class DeviceInfo(BaseModel):
    device_type: str  # 예: "mobile" 또는 "desktop"
    client: str       # 예: "iOS", "Android", "Web


class SessionResponse(BaseModel):
    id: int
    user_id: int
    device_id: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool


class SessionDetailResponse(BaseModel):
    id: int
    user_id: int
    device_id: str
    issued_at: datetime
    expires_at: datetime
    revoked: bool
    device_info: Optional[DeviceInfo] = None
    last_activity: datetime