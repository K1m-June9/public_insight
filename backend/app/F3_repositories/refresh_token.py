# from sqlalchemy import select, update, delete
# from sqlalchemy.ext.asyncio import AsyncSession
# from datetime import datetime
# from typing import Optional, List

# from app.F5_core.logger import security_logger
# from app.F7_models.refresh_token import RefreshToken


# class RefreshTokenRepository:
#     """
#     Refersh Token 관련 DB 작업을 담당하는 리포지토리 클래스
#     - 토큰 조회, 무효화, 삭제, 재사용 감지 등 기능 포함
#     """
#     def __init__(self, db: AsyncSession):
#         self.db = db

#     async def get_by_user_id(self, user_id: str) -> List[RefreshToken]:
#         """
#         특정 사용자 ID로 발급된 모든 리프레시 토큰 조회
#         """
#         result = await self.db.execute(
#             select(RefreshToken)
#             .where(RefreshToken.user_id == user_id)
#             .order_by(RefreshToken.issued_at.desc())
#         )
#         return result.scalars().all()


#     async def get_by_token(self, token: str) -> Optional[RefreshToken]:
#         """
#         리프레시 토큰으로 토큰 정보 조회 (만료된 토큰 제외)
#         - 로그인 시 제공된 Refresh Token이 유효한지 확인할 때 사용
#         - Args:
#             - token (str): 조회할 리프레시 토큰 문자열
#         - Returns: 
#             - Optional[RefreshToken]: 해당 토큰 객체 또는 None
#         """
#         result = await self.db.execute(
#             select(RefreshToken)
#             .where(
#                 RefreshToken.token == token,
#                 RefreshToken.expires_at > datetime.utcnow() # 만료되지 않은 토큰만
#             )
#         )
#         return result.scalar_one_or_none()


#     async def get_latest_token(self, user_id: str) -> Optional[RefreshToken]:
#         """
#         특정 사용자의 최신 발급 토큰을 조회
#         - 재사용 감지 로직에서 비교용으로 사용
#         - Args: 
#             - user_id (int): 사용자 ID
#         - Returns: 
#             - Optional[RefreshToken]: 가장 최근 발급된 토큰 객체

#         """
#         result = await self.db.execute(
#             select(RefreshToken)
#             .where(RefreshToken.user_id == user_id)
#             .order_by(RefreshToken.issued_at.desc()) # 최신순 정렬
#             .limit(1)
#         )
#         return result.scalar_one_or_none()

#     async def revoke_token(self, token: str) -> int:
#         """
#         특정 리프레시 토큰 무효화 처리
#         - Args: 
#             - token (str): 무효화할 토큰 문자열
#         - Returns: 
#             - int: 무효화된 행 수
#         """
#         result = await self.db.execute(
#             update(RefreshToken)
#             .where(RefreshToken.token == token)
#             .values(revoked=True)
#         )
#         await self.db.commit()
#         return result.rowcount

#     async def revoke_all_for_user(self, user_id: str) -> int:
#         """
#         특정 사용자의 모든 리프레시 토큰 무효화 (예: 로그아웃 All Devices)
#         - Args: 
#             - user_id (int): 사용자 ID
#         - Returns: 
#             - int: 무효화된 토큰 수
#         """
#         result = await self.db.execute(
#             update(RefreshToken)
#             .where(RefreshToken.user_id == user_id)
#             .values(revoked=True)
#         )
#         await self.db.commit()
#         return result.rowcount

#     async def delete_expired_tokens(self) -> int:
#         """
#         현재 시간 기준 만료된 리프레시 토큰 삭제
#         - Returns:
#             - int: 삭제된 토큰 수
#         """
#         result = await self.db.execute(
#             delete(RefreshToken)
#             .where(RefreshToken.expires_at < datetime.utcnow())
#         )

#         await self.db.commit()
#         return result.rowcount

#     async def detect_reuse(self, token: str, user_id: str) -> bool:
#         """
#         리프레시 토큰 재사용 감지
#         - 최신 토큰과 일치하지 않으면 재사용으로 간주하고 모든 세션 무효화 + 보안 로그 기록
#         - Args:
#             - token (str): 현재 요청에 사용된 토큰
#             - user_id (int): 사용자 ID
#         - Returns:
#             - bool: 재사용 감지 시 True, 아니면 False
#         """

#         latest_token = await self.get_latest_token(user_id)

#         if latest_token and latest_token.token != token and not latest_token.revoked:
#             # 재사용 의심 토큰 -> 전체 토큰 무효화 + 보안 로그 기록
#             await self.revoke_all_for_user(user_id)
#             await self.log_security_event(
#                 user_id=user_id,
#                 event_type="TOKEN_REUSE",
#                 metadata={
#                     "used_token_suffix": token[-6:],    #보안상 전체 토큰 노출 방지
#                     "detected_at": datetime.utcnow().isoformat() # 감지 시간 기록
#                 }
#             )
#             return True
#         return False

#     async def log_security_event(self, user_id: str, event_type: str, metadata: dict) -> None:
#         """
#         보안 이벤트 로그 기록(예: 재사용, 탈취 시도)
#         - Args:
#             - user_id (int): 사용자 ID
#             - event_type (str): 이벤트 유형 (예: TOKEN_REUSE)
#             - metadata (dict): 추가 정보 (예: 사용된 토큰 일부, 감지 시각 등)
#         """
#         security_logger.warning(
#             f"Security event - user:{user_id}, type:{event_type}",
#             extra={"metadata": metadata}
#         )