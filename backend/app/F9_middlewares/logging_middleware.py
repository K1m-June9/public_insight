import logging
import time
from fastapi import FastAPI, Request, Depends, Query
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# =========================
# 로거 설정
# =========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app.middleware.logging")

# =========================
# 미들웨어 정의
# =========================
class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 요청 처리
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000  # 밀리초

        # 사용자 정보 가져오기
        user_id = getattr(request.state, "user_id", "anonymous")

        # ECS 형식 로그 데이터 구성
        log_extra = {
            "event": {
                "duration": int(process_time * 1_000_000)  # 나노초
            },
            "http": {
                "request": {"method": str(request.method)},
                "response": {"status_code": response.status_code}
            },
            "url": {"path": str(request.url.path)},
            "client": {"ip": request.client.host if request.client else "unknown"},
            "user": {"id": str(user_id)}
        }

        # Query Parameter도 기록
        if request.url.query:
            log_extra["url"]["query"] = str(request.url.query)

        message = f"HTTP {request.method} {request.url.path} - {response.status_code}"

        # 상태코드별 로그 레벨
        if response.status_code >= 500:
            logger.error(message, extra=log_extra)
        elif response.status_code >= 400:
            logger.warning(message, extra=log_extra)
        else:
            logger.info(message, extra=log_extra)

        return response