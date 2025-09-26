import logging
import time
import uuid
from functools import wraps
from fastapi import Request
from typing import Optional 

from app.F5_core.security import auth_handler
from app.F7_models.users import User

logger = logging.getLogger("app.decorator.logging")

def log_event_detailed(action: str, category: list[str] = None):
    """
    API 엔드포인트의 시작/종료(성공/실패)를 기록하는 데코레이터
    - action: 로그에서 식별할 이벤트 이름(예: "LOGIN", "GET_PROFILE")
    - category: 로그의 분류(리스트), Kibana나 ELK에서 필터링할 때 유용

    - 로그인된 사용자가 있으면 user_id, role 기록
    - 아니면 "unknown" 기록

    동작:
    1. wrapper가 호출되면 Request/현재 사용자 정보를 안전하게 추출
    2. 현재 사용자가 함수 인자로 전달되면 그걸 우선 사용
    3. 없다면 Authorization 헤더(Access Token)를 디코딩해서 user_id/role을 추출 시도
    4. 추출 결과를 기반으로 시작 로그, 성공/실패 로그를 JSON 필드(extra)에 담아 기록
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # --- 1. Request 객체 찾기 ---
            # args에 Request가 있는지 먼저 찾고, 없으면 kwargs에서 'request' 키를 확인
            request: Optional[Request] = next((arg for arg in args if isinstance(arg, Request)), None)
            if request is None: 
                request=kwargs.get("request")
                if not isinstance(request, Request):
                    request = None 

            # --- 2. current_user가 인자로 전달되었는지 확인 ---
            current_user = next((arg for arg in args if isinstance(arg, User)), None)
            if current_user is None:
                # kwargs에 'current_user'로 들어올 수도 있으므로 체크
                current_user = kwargs.get("current_user")
                if not isinstance(current_user, User):
                    current_user = None

            # --- 3. 기본 사용자 정보 초기값 설정 ---
            user_id = "unknown"
            role = "unknown"

            # -- 3-1. 만약 current_user가 있으면 우선 사용(DB로부터 얻은 User 객체 --
            if current_user: 
                user_id = getattr(current_user, "user_id", "unknown")
                role = getattr(current_user, "role", "unknown")

            # -- 3-2. current_user가 없고 Request가 있으면 Authorization 헤더에서 Access Token 파싱 시도
            elif request:
                auth_header = request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ", 1)[1].strip()
                    # auth_handler.decode_access_token은 Access Token 유효성 검증 및 payload 반환
                    payload = auth_handler.decode_access_token(token)
                    if payload:
                        # JWT payload 표준: sub로 사용자 식별자를 담는 관례
                        user_id = payload.get("sub", "unknown")
                        # role이 enum 값으로 들어있을 수도 있으니 그대로 기록(문자열 또는 enum.value)
                        role = payload.get("role", "unknown")


            # --- 4. 로그에 공통으로 담을 기본 정보 구성 ---
            # trace id: 요청 단위로 고유 id를 만ㄷ르어 추적에 활용
            # client IP, user-agent: 운영에서 유용
            start_time = time.perf_counter()
            trace_id = str(uuid.uuid4())
            
            # request.client는 없을 수도 있으므로 안전하게 접근
            client_ip = "unknown"
            try:
                if request and getattr(request, "client", None):
                    client_ip = request.client.host or "unknown"
            except Exception:
                client_ip = "unknown"

            user_agent = "unknown"
            try:
                if request:
                    user_agent = request.headers.get("user-agent", "unknown")
            except Exception:
                user_agent = "unknown"

            request_method = request.method if request else "unknown"
            request_path = request.url.path if request else "unknown"
            request_query = str(request.url.query) if request and request.url.query else None

            base_log_extra = {
                "trace": {"id": trace_id},
                "event": {"action": action, "category": category or ["custom"]},
                "user": {"id": user_id, "role": role},
                "client": {"ip": client_ip},
                "http": {
                    "request": {
                        "method": request_method,
                        "user_agent": user_agent
                    }
                },
                "url": {
                    "path": request_path,
                    "query": request_query
                }
            }


            # --- 5. 함수 실행 전/후로 로그 기록 ---
            # 시작 로그: type: start 
            # 성공 로그: type: end, outcome: success 
            # 실패 로그: type: end, outcome: failure, error 포함
            try:
                # 시작 로그: 여기서는 extra에 JSON 구조를 담아 ELK로 전송할 수 있게 함
                start_log = {
                    "json_fields": {
                        **base_log_extra,
                        "event": {**base_log_extra["event"], "type": "start"}
                    }
                }
                # 실제 로깅
                logger.info(f"Action '{action}' started.", extra=start_log)

                # --- 원래 엔드포인트 함수 실행 ---
                result = await func(*args, **kwargs)

                # 성공 로그: 실행 시간 측정 포함
                duration_ms = (time.perf_counter() - start_time) * 1000
                success_log = {
                    "json_fields": {
                        **base_log_extra,
                        "event": {**base_log_extra["event"], "type": "end", "outcome": "success", "duration_ms": round(duration_ms, 2)}
                    }
                }
                logger.info(f"Action '{action}' finished successfully.", extra=success_log)
                return result

            except Exception as e:
                # 실패 로그: 예외 정보 포함
                duration_ms = (time.perf_counter() - start_time) * 1000
                failure_log = {
                    "json_fields": {
                        **base_log_extra,
                        "event": {**base_log_extra["event"], "type": "end", "outcome": "failure", "duration_ms": round(duration_ms, 2)},
                        "error": {"type": e.__class__.__name__, "message": str(e)}
                    }
                }
                # exc_info=True로 스택트레이스도 로깅 (Elasticsearch로 전송 시에는 메시지 길이/용량 주의)
                logger.error(f"Action '{action}' failed.", exc_info=True, extra=failure_log)
                # 원래 예외를 다시 던져서 FastAPI가 적절히 처리하게 함
                raise e

        return wrapper
    return decorator
