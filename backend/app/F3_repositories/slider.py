from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional, List
import logging
from app.F7_models.sliders import Slider

logger = logging.getLogger(__name__)

class SliderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 활성화된 슬라이더 목록 조회 메서드
    # 입력: 
    #   current_time - 현재 시간 (datetime 객체, 선택적)
    # 반환: 
    #   활성화된 Slider 객체들의 리스트
    # 설명: 
    #   is_active가 True이고, 현재 시간이 노출 기간(start_date ~ end_date) 내에 있는 슬라이더들을 
    #   display_order 오름차순으로 정렬하여 반환
    #   start_date나 end_date가 NULL인 경우 해당 조건은 무시 (날짜 제한 없음)
    async def get_active_sliders(self, current_time: Optional[datetime] = None) -> List[Slider]:
        query = select(Slider).where(Slider.is_active == True)
        
        # 현재 시간이 제공된 경우에만 날짜 조건 추가
        if current_time:
            # start_date가 NULL이거나 현재 시간보다 이전/같음
            query = query.where(
                (Slider.start_date.is_(None)) | (Slider.start_date <= current_time)
            )
            # end_date가 NULL이거나 현재 시간보다 이후/같음
            query = query.where(
                (Slider.end_date.is_(None)) | (Slider.end_date >= current_time)
            )
        
        # display_order 기준 오름차순 정렬
        query = query.order_by(Slider.display_order.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    # ID를 기준으로 활성화된 슬라이더 상세 조회 메서드
    # 입력: 
    #   slider_id - 조회할 슬라이더의 고유 식별자 (int)
    #   current_time - 현재 시간 (datetime 객체, 선택적)
    # 반환: 
    #   조회된 Slider 객체 또는 None (조건에 맞지 않거나 존재하지 않는 경우)
    # 설명: 
    #   주어진 ID의 슬라이더를 조회하되, 다음 조건을 모두 만족하는 경우에만 반환
    #   - is_active가 True (활성화 상태)
    #   - 현재 시간이 노출 기간(start_date ~ end_date) 내에 있음
    #   - start_date나 end_date가 NULL인 경우 해당 조건은 무시 (날짜 제한 없음)
    #   모든 조건을 WHERE절에서 동시에 처리하여 쿼리 효율성 최적화
    async def get_slider_by_id(self, slider_id: int, current_time: Optional[datetime] = None) -> Optional[Slider]:
        query = select(Slider).where(
            Slider.id == slider_id,
            Slider.is_active == True
        )
        
        # 현재 시간이 제공된 경우에만 날짜 조건 추가
        if current_time:
            # start_date가 NULL이거나 현재 시간보다 이전/같음
            query = query.where(
                (Slider.start_date.is_(None)) | (Slider.start_date <= current_time)
            )
            # end_date가 NULL이거나 현재 시간보다 이후/같음
            query = query.where(
                (Slider.end_date.is_(None)) | (Slider.end_date >= current_time)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()