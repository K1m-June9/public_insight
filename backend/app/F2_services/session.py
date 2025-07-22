from typing import List, Optional
from fastapi import HTTPException

from app.F3_repositories.session import SessionRepository
from app.F5_core.redis import RedisManager
from app.F6_schemas.session import SessionResponse, SessionDetailResponse, DeviceInfo
from app.F7_models.refresh_token import RefreshToken


class SessionService:
    def __init__(self, repo: SessionRepository):
        # 세션 관련 DB 작업을 담당하는 Repository 주입
        self.repo = repo

    # /reset-password 사용
    # 모두 로그아웃
    async def revoke_all_sessions(self, user_id: str):
        """
        사용자의 모든 세션을 무효화
        - DB: refresh_token.revoked=True 처리
        - Redis: user_tokens:{user_id}: * 형식의 모든 키 제거
        """
        await self.repo.revoke_all_for_user(user_id)

        cursor = 0
        pattern = f"user_tokens:{user_id}:*"
        while True:
            # Redis 키들을 SCAN 명령으로 순차 검색 및 삭제
            cursor, keys = await RedisManager.scan_keys(cursor=cursor, pattern=pattern)
            if keys:
                await RedisManager.delete_keys(keys)
            if cursor == 0 or cursor == b'0':
                break # 모든 키 삭제 완료


    # 비밀번호 변경 -> 현재 기기의 Refresh Token 제외 모두 무효화 -> Redis Access Token 삭제
    # 현재 기기 제외 모두 로그아웃
    async def  logout_other_sessions(self, user_id: str, current_jti: str, current_refresh_token: str):
        """
        현재 기기 제외 모든 세션 로그아웃 처리

        - Redis: 현재 기기의 jti를 제외한 모든 access token 관련 키 삭제
        - DB: 현재 refresh token을 제외한 모든 refresh token을 revoked 처리
        """

        # --- Redis 처리 ---
        # Redis 키 패턴: user_tokens:{user_id}:{jti}
        cursor = 0
        pattern = f"user_tokens:{user_id}:*"

        while True:
            # Redis에서 해당 패턴의 키 검색 (SCAN 명령 사용)
            cursor, keys = await RedisManager.scan_keys(cursor=cursor, pattern=pattern)

            keys_to_delete = []
            for key in keys:
                try:
                    # bytes -> str 안전하게 변환
                    key_str = key.decode() if isinstance(key, bytes) else key
                except Exception:
                    continue

                if current_jti in key_str:
                    continue # 현재 세션(jti)은 유지하므로 제외
                
                parts = key_str.split(":")
                if len(parts) != 3:
                    continue 
                # 키에서 jti 추출

                _, _, jti = parts

                # 삭제 대상 키 목록에 추가
                keys_to_delete.append(key_str)  # user_tokens:{user_id}:{jti}
                keys_to_delete.append(f"access_token:{jti}")  # access_token:{jti}

            # 일괄 삭제
            if keys_to_delete:
                await RedisManager.delete_keys(keys_to_delete)

            # cursor가 0이면 스캔 완료
            if cursor == 0 or cursor == b"0":
                break

        # --- DB 처리 ---
        # 현재 refresh_token을 제외한 모든 토큰을 revoked=True 처리
        await self.repo.revoke_all_for_user_except(user_id, current_refresh_token)


    #==============================
    # 내부 유틸 메서드
    #==============================    


    def _to_session_detail_response(self, token: RefreshToken) -> SessionDetailResponse:
        """
        RefreshToken 모델 인스턴스를 상세 응답 객체로 변환
        - ast_activity는 마지막 사용 시각 또는 최초 발급 시각
        """
        return SessionDetailResponse(
            id=token.id,
            user_id=token.user_id,
            device_id=token.device_id,
            issued_at=token.issued_at,
            expires_at=token.expires_at,
            revoked=token.revoked,
            device_info=self._parse_device_info(token.device_id),
            last_activity=token.last_used_at or token.issued_at
        )

    def _parse_device_info(self, device_id: str) -> DeviceInfo:
        d = device_id.lower()
        return DeviceInfo(
            device_type="mobile" if "mob" in d else "desktop",
            client="iOS" if "ios" in d else "Android" if "and" in d else "Web"
        )









    # async def get_user_sessions(self, user_id: str) -> List[SessionResponse]:
    #     """특정 사용자(user_id)의 모든 세션 정보를 간략한 형태로 조회"""
        
    #     # 예시: '내 세션 목록' 화면 등
    #     tokens = await self.repo.get_by_user_id(user_id)
    #     return [
    #         SessionResponse(
    #             id=token.id,
    #             user_id=token.user_id,
    #             device_id=token.device_id,
    #             issued_at=token.issued_at,
    #             expires_at=token.expires_at,
    #             revoked=token.revoked
    #         )
    #         for token in tokens
    #     ]

    # async def get_sessions(
    #     self,
    #     user_id: Optional[str] = None,
    #     active_only: bool = True
    # ) -> List[SessionDetailResponse]:
    #     """
    #     조건에 따라 세션 목록을 상세 정보 형태로 조회
    #     - admin 기능 등에서 전체 사용자 조회를 지원 가능
    #     - active_only=True: revoked=False 필터링 적용
    #     """
    #     tokens = await self.repo.get_sessions(user_id=user_id, active_only=active_only)
    #     return [self._to_session_detail_response(token) for token in tokens]

    # async def revoke_session(self, session_id: int):
    #     """
    #     특정 세션 ID를 무효화 (revoked=True)처리
    #     해당 세션과 연관된 Redis access token 키 제거
    #     """
    #     token = await self.repo.get_by_id(session_id)
    #     if not token:
    #         raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    #     token.revoked = True
    #     # 여기 수정
    #     #await self.repo.commit()

    #     await RedisManager.delete_access_token(token.token)
    #     await RedisManager.delete_user_token_key(str(token.user_id), token.token)


    # async def revoke_user_session(self, session_id: int, user_id: str):
    #     """
    #     사용자의 특정 세션 무효화 (본인 여부 검증 포함)
    #     - 타인의 세션에 접근 시도하면 403 처리
    #     """
    #     token = await self.repo.get_by_id(session_id)
    #     if not token:
    #         raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")
    #     if token.user_id != user_id:
    #         raise HTTPException(status_code=403, detail="권한이 없습니다")

    #     await self.revoke_session(session_id)