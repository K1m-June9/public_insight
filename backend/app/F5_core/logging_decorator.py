import logging
from functools import wraps
from fastapi import Request

logger = logging.getLogger("app.decorator.logging")

def log_event_detailed(action: str, category: list[str] = None):
    """
    특정 비즈니스 로직 함수의 시작, 성공, 실패를 상세하게 로깅하는 데코레이터.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request | None = kwargs.get("request")
            current_user = kwargs.get("current_user")
            
            log_extra = {
                "event": {"action": action, "category": category or ["custom"]},
                "user": {"id": current_user.user_id if current_user else "unknown"},
                "client": {"ip": request.client.host if request else "unknown"}
            }

            try:
                # 함수 시작 로그
                log_extra["event"]["type"] = ["start"]
                logger.info(f"Action '{action}' started.", extra=log_extra)
                
                # 원래 함수 실행
                result = await func(*args, **kwargs)
                
                # 함수 성공 로그
                log_extra["event"]["type"] = ["end"]
                log_extra["event"]["outcome"] = "success"
                logger.info(f"Action '{action}' finished successfully.", extra=log_extra)
                
                return result
            except Exception as e:
                # 함수 실패 로그
                log_extra["event"]["type"] = ["end"]
                log_extra["event"]["outcome"] = "failure"
                log_extra["error"] = {"type": e.__class__.__name__, "message": str(e)}
                logger.error(
                    f"Action '{action}' failed with an exception.",
                    exc_info=True,
                    extra=log_extra
                )
                raise e
        return wrapper
    return decorator