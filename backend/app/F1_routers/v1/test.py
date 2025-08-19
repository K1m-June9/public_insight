from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.F5_core.logging_decorator import log_event_detailed
from app.F5_core.dependencies import verify_active_user
from app.F7_models.users import User

router = APIRouter()

# User = Depends(verify_active_user) 중요

@router.get("/ping")
@log_event_detailed(action="PING", category=["TEST"])
async def ping_active_user(current_user: User = Depends(verify_active_user)):
    """
    Access Token이 유효하고, 계정이 활성 상태일 때만 접근 가능한 테스트 API
    """
    return JSONResponse(status_code=200, content={"success": True})
