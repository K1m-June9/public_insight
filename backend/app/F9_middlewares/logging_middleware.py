import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# 이 미들웨어 전용 로거를 생성합니다.
logger = logging.getLogger("app.middleware.logging")

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # 다음 미들웨어 또는 라우터 함수를 호출합니다.
        response = await call_next(request)
        
        process_time = (time.time() - start_time) * 1000  # 밀리초
        
        # 의존성 주입 단계에서 request.state에 저장된 사용자 정보를 가져옵니다.
        user_info = getattr(request.state, "user", None)
        user_id = user_info.user_id if user_info else "anonymous"

        # ECS 형식에 맞는 구조화된 로그 데이터를 구성합니다.
        log_extra = {
            "event": {
                "duration": int(process_time * 1_000_000) # ECS는 나노초 단위
            },
            "http": {
                "request": {"method": str(request.method)},
                "response": {"status_code": response.status_code}
            },
            "url": { "path": str(request.url.path) },
            "client": { "ip": request.client.host if request.client else "unknown" },
            "user": { "id": user_id }
        }
        
        message = f"HTTP {request.method} {request.url.path} - {response.status_code}"

        # 응답 상태 코드에 따라 로그 레벨을 동적으로 결정합니다.
        if response.status_code >= 500:
            logger.error(message, extra=log_extra)
        elif response.status_code >= 400:
            logger.warning(message, extra=log_extra)
        else:
            logger.info(message, extra=log_extra)
        
        return response