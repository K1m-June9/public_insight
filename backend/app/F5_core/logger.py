### 임시 ###
import logging
from datetime import datetime
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.F7_models.token_security_event_logs import TokenSecurityEventLog
from app.F5_core.config import settings

# 기본 로거 설정 (한 번만 설정)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)

security_logger = logging.getLogger("app.security")
security_logger.propagate = False

if not security_logger.hasHandlers():
    security_handler = logging.FileHandler("security.log", encoding="utf-8")
    security_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    security_logger.addHandler(security_handler)


async def log_token_event(
    event_type: str, metadata: Dict[str, Any], db: AsyncSession
) -> None:
    """
    토큰 관련 이벤트를 비동기적으로 로깅 (콘솔, 보안 로그 파일, 운영환경일 때만 DB)
    
    Args:
        event_type (str): 이벤트 타입 (예: "TOKEN_ISSUED", "TOKEN_REVOKED")
        metadata (Dict[str, Any]): 이벤트 관련 추가 정보
        db (AsyncSession): 비동기 DB 세션
    """
    try:
        # 민감정보 마스킹
        safe_metadata = {
            k: v if k not in ["token", "refresh_token"] else f"{str(v)[:2]}***{str(v)[-2:]}"
            for k, v in metadata.items()
        }

        # 콘솔, 보안 로그 기록
        logger.info(f"Token Event - {event_type}: {safe_metadata}")
        security_logger.info(f"Token {event_type} - {safe_metadata}")

        # 운영 환경에서만 DB에 로그 저장
        if settings.ENVIRONMENT == "production":
            token_log = TokenSecurityEventLog(
                event_type=event_type,
                metadata=safe_metadata,
                timestamp=datetime.utcnow(),
            )
            db.add(token_log)
            await db.commit()

    except Exception as e:
        logger.error(f"Failed to log token event: {e}", exc_info=True)
        await db.rollback()

"""
[사용방법]
토큰 발급 이벤트 로깅
    await log_token_event(
        event_type="TOKEN_ISSUED",
        metadata={"user_id": user_id, "token": token},
        db=db
    )
"""
