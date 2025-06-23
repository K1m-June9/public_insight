from fastapi import Response 
from app.F5_core.config import settings 

def set_refresh_token_cookie(response: Response, refresh_token: str):
    """Refresh Token을 HttpOnly 쿠키에 저장하는 함수"""
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.SECURE_COOKIE,
        samesite="lax" if settings.IS_LOCAL else "strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v1/auth/refresh",
    )