from sqlalchemy import select, update, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import logging
from app.F7_models.users import User, UserStatus
from app.F7_models.refresh_token import RefreshToken

logger = logging.getLogger(__name__)

class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # user_id(사용자 아이디)를 기준으로 User 객체를 DB에서 조회하는 함수
    # 입력: user_id
    # 반환: User 객체 또는 조회 실패 시 None
    async def get_user_by_user_id(self, user_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    # 사용자 기본키(user_pk)를 기준으로 User 객체를 조회하는 메서드
    # 입력: user_pk - 조회할 사용자의 고유 식별자 (int)
    # 반환: User 객체 또는 None
    async def get_user_by_id(self, user_pk: int) -> Optional[User]:
        return await self.db.get(User, user_pk)

    # RefreshToken 객체를 DB에 저장하는 메서드
    # 입력: token - 저장할 refreshToken 인스턴스
    # 반환: None(저장 성공 시 별도 반환값 없음)
    # 트랙잭션 커밋 도중 오류 발생 시 롤백하고 예외를 다시 발생시킴
    async def add_refresh_token(self, token: RefreshToken) -> None:
        self.db.add(token)
        try:
            await self.db.commit()
        except Exception:
            await self.db.rollback() # 오류 시 변경사항 롤백
            raise # 예외를 상위 호출자에게 전달


    # RefreshToken 조회 메서드
    # 입력: 
    #   token_str - 조회할 Refresh Token 문자열 (UUID 형태)
    #   device_id - 토큰이 발행된 디바이스 식별자 (해시값)
    # 반환: 
    #   조회된 RefreshToken 객체 또는 없으면 None
    #   설명: token_str과 device_id가 모두 일치하는 RefreshToken 레코드를 DB에서 조회함
    async def get_refresh_token(self, token_str: str, device_id: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token_str,
                RefreshToken.device_id == device_id,
                RefreshToken.revoked.is_(False)
            )
        )
        return result.scalar_one_or_none()


    # 단일 RefreshToken 무효화 메서드(트랙젝션 롤백 포함)
    # 입력: 
    #   token_str - 무효화할 Refresh Token 문자열 (UUID 형태)
    # 반환: 없음
    # 설명: 지정된 token_str에 해당하는 RefreshToken 레코드를 revoked=True로 업데이트하여 무효화 처리
    async def revoke_refresh_token(self, token_str: str, device_id: str) -> None:
        try:
            result = await self.db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.token == token_str,
                    RefreshToken.device_id == device_id,
                    RefreshToken.revoked == False
                )
                .values(revoked=True)
            )
            if result.rowcount == 0:
                logger.warning(f"Attempt to revoke non-existent or already revoked token: {token_str} on device {device_id}")
            await self.db.commit()
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to revoke refresh token {token_str} on device {device_id}: {e}", exc_info=True)
            raise

    # 특정 디바이스에 속한 RefreshToken 무효화 메서드(트랜잭션 롤백 포함)
    # 입력:
    #   user_id - 사용자 고유 ID (정수)
    #   device_id - 디바이스 고유 식별자 (해시 문자열)
    # 반환: 없음
    # 설명: 주어진 사용자(user_id)와 디바이스(device_id)에 속하며, 아직 무효화되지 않은(revoked=False) 모든 RefreshToken을 revoked=True로 설정하여 무효화 처리
    async def revoke_device_refresh_tokens(self, user_id: str, device_id: str) -> None:
        try:
            await self.db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.device_id == device_id,
                    RefreshToken.revoked.is_(False)
                ).values(revoked=True)
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise


    # 사용자의 모든 활성 RefreshToken 무효화 메서드 (트랜잭션 롤백 포함)
    # 입력:
    #   user_id - 사용자 고유 ID (문자열)
    # 반환: 없음
    # 설명: 주어진 사용자(user_id)에 대해 아직 무효화되지 않은 모든 RefreshToken을 revoked=True로 설정하여 모두 무효화 처리
    async def revoke_all_user_refresh_tokens(self, user_id: str) -> None:
        try:
            await self.db.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked.is_(False)
                )
                .values(revoked=True)
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise


    # 만료된 RefreshToken 일괄 삭제 (운영용 정리 기능)
    # 입력: 없음
    # 반환: 없음
    # 설명: DB에서 expires_at이 현재 시간보다 이전인 만료된 RefreshToken들을 모두 삭제
    # 트랜잭션 오류 발생 시 롤백 처리 포함
    async def delete_expired_refresh_tokens(self) -> None:
        try:
            await self.db.execute(
                delete(RefreshToken)
                .where(RefreshToken.expires_at < datetime.utcnow())
            )
            await self.db.commit()
        except Exception:
            await self.db.rollback()
            raise
    

    
    # user_id 중복 여부 확인
    async def is_user_id_exists(self, user_id: str) -> bool:
        """user_id 중복 여부 확인"""
        stmt = select(exists().where(User.user_id == user_id))
        return await self.db.scalar(stmt)

    # email 중복 여부 확인
    async def is_email_exists(self, email: str) -> bool:
        """email 중복 여부 확인"""
        stmt = select(exists().where(User.email == email))
        return await self.db.scalar(stmt)

    
    # nickname 중복 여부 확인
    async def is_nickname_exists(self, nickname: str) -> bool:
        stmt = select(exists().where(User.nickname == nickname))
        return await self.db.scalar(stmt)
    

    # 새로운 사용자 등록
    async def save_user(self, user: User):
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)


    # 아이디 찾기 - 이메일을 통해 user_id 
    async def find_user_id_by_email(self, email: str) -> str:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()


    # 이메일과 user_id를 동시에 만족하는 사용자 조회
    async def get_user_by_email_and_id(self, email: str, user_id: str):
        result = await self.db.execute(
            select(User).where(
                (User.email == email) & (User.user_id == user_id)
            )
        )
        return result.scalar_one_or_none()


    # 이메일과 user_id를 동시에 만족하는 사용자의 비밀번호 변경
    async def update_password(self,user_id: str, email: str, hashed_password:str):
        # 1. user_id와 email이 일치하는 사용자 조회
        result = await self.db.execute(
            select(User).where(
                (User.email == email) & (User.user_id == user_id)
            )
        )
        user = result.scalar_one_or_none()

        # 2. 사용자가 존재하지 않으면 예외 발생
        if not user:
            raise ValueError("해당 사용자를 찾을 수 없습니다.")
        
        # 3. 비밀번호 해시값 업데이트
        user.password_hash = hashed_password

        # 4. 변경사항 커밋
        await self.db.commit()
