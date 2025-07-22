from sqlalchemy import select, update, delete, exists, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import logging

from app.F7_models.notices import Notice

logger = logging.getLogger(__name__)

class NoticeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetch_pinned_notice(self):
        """
        활성화된 고정된 공지사항 목록 조회
        - 조건: is_active=True, is_pinned=True
        - 정렬: created_at 기준 내림차순 (최신 공지 우선)
        - 반환: 딕셔너리 리스트
        """
        stmt = select(
            Notice.id,
            Notice.title,
            Notice.author,
            Notice.view_count,
            Notice.created_at,
            Notice.is_pinned
        ).where(
            # 2. 활성화 상태이며 고정된 공지사항만 필터링
            Notice.is_active == True,    # 비활성화된 공지 계획
            Notice.is_pinned == True
            
        ).order_by(
            # 3. 작성일 내림차순 정렬 (최신)
            Notice.created_at.desc()    # 작성일 기준 내림차순 정렬
        )
        
        # 4. 비동기 쿼리 실행
        result = await self.db.execute(stmt)

        # 5. 결과를 모두 가져옴
        rows = result.fetchall()
        
        # 6. Row 객체들을 Dict 형태로 변환
        notices_data = []
        for row in rows:
            notice_dict = {
                'id': row.id,
                'title': row.title,
                'created_at': row.created_at,
            }
            notices_data.append(notice_dict)
        
        # 7. 결과 반환
        return notices_data
    
    # 공지사항 조회 메서드
    async def get_notices_with_details(self):
        """
        활성화된 공지사항 목록 조회
        - 고정 공지를 우선 정렬
        - 작성일 기준으로 최신 순 정렬
        """
        stmt = select(
            Notice.id,
            Notice.title,
            Notice.author,
            Notice.view_count,
            Notice.created_at,
            Notice.is_pinned
        ).where(
            Notice.is_active == True    # 비활성화된 공지 계획
        ).order_by(
            Notice.is_pinned.desc(),    # 고정 공지 먼저 정렬
            Notice.created_at.desc()    # 작성일 기준 내림차순 정렬
        )
        
        result = await self.db.execute(stmt)
        rows = result.fetchall()
        
        # Row 객체들을 Dict 형태로 변환
        notices_data = []
        for row in rows:
            notice_dict = {
                'id': row.id,
                'title': row.title,
                'author': row.author,
                'is_pinned': row.is_pinned,
                'view_count': row.view_count,
                'created_at': row.created_at,
            }
            notices_data.append(notice_dict)
        
        return notices_data


    async def get_notice_by_id(self, notice_id: int) -> Optional[Notice]:
        """
        주어진 ID에 해당하는 활성화된 공지사항 조회
        """
        stmt = select(Notice).where(
            and_(
                Notice.id == notice_id,
                Notice.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def increment_notice_view_count(self, notice_id: int) -> bool:
        """
        주어진 공지사항의 조회수를 1 증가
        - 비활성화된 공지사항에는 적용 x
        - 조회 성공 시 True, 실패 시 False 반환
        """
        stmt = (
            update(Notice)
            .where(
                and_(
                    Notice.id == notice_id,
                    Notice.is_active == True
                )
            )
            .values(view_count=Notice.view_count + 1)
        )

        try:
            # 업데이트
            result = await self.db.execute(stmt)
            await self.db.commit()

            # 업데이트되었다면 True 반환
            if result.rowcount > 0:
                logger.info(f"공지사항 조회수 증가 성공 - notice_id: {notice_id}")
                return True
            else:
                logger.warning(f"조회수 증가 실패 - 해당 공지 없음: notice_id: {notice_id}")
                return False
        except Exception as e:
            await self.db.rollback()
            logger.warning(f"공지사항 조회수 증가 중 오류 발생 - notice_id: {notice_id}, error: {str(e)}")
            return False