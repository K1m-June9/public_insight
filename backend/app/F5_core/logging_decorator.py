import logging
from functools import wraps
from fastapi import Request
import time
import uuid

from app.F7_models.users import User

logger = logging.getLogger("app.decorator.logging")

def log_event_detailed(action: str, category: list[str] = None):
    """
    API 엔드포인트 함수의 실행 전후로 상세한 정보를 포함한 로그를 자동으로 기록하는 데코레이터.
    - 주요 정보: Trace ID, 사용자 정보, 요청 정보, 처리 시간, 성공/실패 여부 등
    - 로그 형식: ECS(Elastic Common Schema)를 따라 구조화하여 로그 분석 시스템과의 연동을 요이하게 함
    
    :param action: 로깅할 에빈트의 구체적인 행위
    :param category: 이벤트의 기능적 분류
    """
    # 데코레이터 로직을 감싸는 외부 함수
    def decorator(func):
        # @wraps(func)는 데코레이터가 적용된 함수의 메타데이터(이름, 독스트링)를 보존
        # 디버깅 시 원래 함수 정보를 잃지 않도록 도와주는 역할
        @wraps(func)

        # 데코레이터가 감쌀 함수(API 엔드포인트 함수)와 동일한 시그니처를 가지는 wrapper
        # *args는 위치 인자들을 튜플로, **kwargs는 키워드 인자들을 딕셔너리로 받음(패킹)
        async def wrapper(*args, **kwargs): # 순서, 키-값
            # --- 1. 인자 목록에서 request와 current_user 객체를 안정적으로 찾기 ---
            # request: API 요청에 대한 모든 정보(헤더, IP 등)를 담고 있음
            request: Request | None = next((arg for arg in args if isinstance(arg, Request)), kwargs.get("request"))

            # User: 인증 미들웨어를 통해 주입된 현재 로그인한 사용자 정보
            current_user: User | None = next((arg for arg in args if isinstance(arg, User)), kwargs.get("current_user"))
            
            # --- 2. 로그에 포함할 풍부한 정보(extra) 구성 ---
            start_time = time.perf_counter() # 함수 실행 시작 시간 기록(정확한 시간 측정용)
            trace_id = str(uuid.uuid4()) # 이 요청/응답 사이클을 고유하게 식별할 ID 생성

            # ECS (Elastic Common Schema) 형식을 참고하여 로그 데이터를 구조화
            # Elasticsearch, Kibana 등에서 데이터를 분석하고 시각화하기 매우 용이함

            base_log_extra = {
                "trace": {"id": trace_id}, # 분산 환경에서 요청의 흐름을 추적하기 위한 ID
                "event": {"action": action, "category": category or ["custom"]}, # 이벤트의 종류와 분류
                "user": {"id": current_user.user_id if current_user else "unknown"}, # 요청을 보낸 사용자 
                "client": {"ip": request.client.host if request else "unknown"}, # 클라이언트 IP 주소
                "http": {
                    "request": {
                        "method": request.method if request else "unknown", # HTTP 메소드 (GET, POST 등)
                        "user_agent": request.headers.get("user-agent") if request else "unknown" # 클라이언트 정보 (브라우저, OS 등)
                    }
                }, 
                "url": {
                    "path": request.url.path if request else "unknown", # 요청 경로 (예: /api/v1/feeds/detail/3070/bookmark)
                    "query": str(request.url.query) if request and request.url.query else None # 쿼리 파라미터
                }
            }

            try:
                # --- 3. 함수 시작 로그 기록 ---
                # 공통 로그 정보(base_log_extra)에 이벤트 타입을 'start'로 추가하여 시작 로그를 구성

                # '**' 연산자를 사용하여 딕셔너리를 병합
                start_log = {"json_fields": {**base_log_extra, "event": {**base_log_extra["event"], "type": "start"}}}

                # 'extra' 인자를 통해 구조화된 로그 데이터를 기록
                logger.info(f"Action '{action}' started.", extra=start_log)
                
                # --- 4. 원래 함수 실행 ---
                # 데코레이터의 핵심 역할: 원래 함수를 호출하고 그 결과를 받아옴
                result = await func(*args, **kwargs)
                
                # --- 5. 함수 성공 로그 ---
                duration_ms = (time.perf_counter() - start_time) * 1000 # 총 실행 시간을 밀리초(ms) 단위로 계산

                # 성공 로그에는 이벤트 타입을 'end', 결과를 'success', 실행시간 추가
                success_log = {
                    "json_fields": {
                        **base_log_extra,
                        "event": {**base_log_extra["event"], "type": "end", "outcome": "success", "duration_ms": round(duration_ms, 2)}
                    }
                }
                logger.info(f"Action '{action}' finished successfully.", extra=success_log)
                
                # 결과 반환
                return result
                
            except Exception as e:
                # --- 6. 함수 실패 로그 ---
                duration_ms = (time.perf_counter() - start_time) * 1000 # 실패까지 걸린 시간 계산 

                # 실패 로그에는 결과를 'failure', 발생한 에러 정보를 추가
                failure_log = {
                    "json_fields": {
                        **base_log_extra,
                        "event": {**base_log_extra["event"], "type": "end", "outcome": "failure", "duration_ms": round(duration_ms, 2)},
                        "error": {"type": e.__class__.__name__, "message": str(e)}
                    }
                }

                # 'exc_info=True'를 설정하여 스택 트레이스까지 함께 로깅
                logger.error(f"Action '{action}' failed.", exc_info=True, extra=failure_log)
                raise e
        return wrapper
    return decorator