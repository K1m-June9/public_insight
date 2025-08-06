from sqlalchemy import select, func, and_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Tuple, Any
import logging

from app.F7_models.categories import Category
from app.F7_models.feeds import Feed, ProcessingStatusEnum
from app.F7_models.organizations import Organization

logger = logging.getLogger(__name__)

class FeedAdminRepository:
    """
    관리자 기능 - 피드 관리 관련 데이터베이스 작업을 처리하는 클래스
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_categories_by_organization(self, organization_id: int) -> List[Category]:
        """
        특정 기관에 속한 활성화된 카테고리 목록을 조회

        Args:
            organization_id (int): 조회할 기관의 ID

        Returns:
            List[Category]: Category ORM 객체들의 리스트
        """
        try:
            stmt = (
                select(Category)
                .where(
                    Category.organization_id == organization_id,
                    Category.is_active == True
                )
                .order_by(Category.name.asc())
            )
            result = await self.db.execute(stmt)
            categories = result.scalars().all()
            return list(categories)
        except Exception as e:
            logger.error(f"Error getting categories for organization {organization_id}: {e}", exc_info=True)
            return []
        
    async def get_feeds_list(
        self,
        page: int,
        limit: int,
        search: Optional[str] = None,
        organization_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        관리자 페이지: 피드 목록을 페이지네이션, 검색, 필터링하여 조회

        Args:
            page (int): 페이지 번호
            limit (int): 페이지당 항목 수
            search (Optional[str]): 제목 검색어
            organization_id (Optional[int]): 기관 ID 필터
            category_id (Optional[int]): 카테고리 ID 필터

        Returns:
            Tuple[List[Dict[str, Any]], int]: (피드 목록, 전체 개수) 튜플
        """
        offset = (page - 1) * limit

        # 기본 쿼리: Feed, Organization, Category 테이블을 JOIN
        base_query = (
            select(
                Feed.id,
                Feed.title,
                Feed.organization_id,
                Organization.name.label("organization_name"),
                Category.name.label("category_name"),
                Feed.is_active,
                # DB에 저장될 Enum 타입의 이름을 가져오기 위해 .name 사용
                #Feed.processing_status.name.label("processing_status"), #현재 Feed 테이블에 processing_status가 없으므로 나중에 마이너 업데이트를 통해 추가
                Feed.view_count,
                Feed.created_at,
            )
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
        )

        # 필터 조건들을 담을 리스트
        filters = []
        if search:
            filters.append(Feed.title.ilike(f"%{search}%"))
        if organization_id:
            filters.append(Feed.organization_id == organization_id)
        if category_id:
            filters.append(Feed.category_id == category_id)

        # 필터가 있으면 쿼리에 추가
        if filters:
            base_query = base_query.where(and_(*filters))

        # 1. 전체 개수를 세는 쿼리
        count_stmt = select(func.count()).select_from(base_query.alias())
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar_one()

        # 2. 실제 데이터를 가져오는 쿼리 (정렬 및 페이지네이션 적용)
        data_stmt = base_query.order_by(Feed.id.desc()).offset(offset).limit(limit)
        data_result = await self.db.execute(data_stmt)
        feeds = data_result.mappings().all() # .mappings()는 결과를 Dict처럼 사용할 수 있게 해줌

        return list(feeds), total_count
    
    async def get_feed_by_id(self, feed_id: int) -> Optional[Dict[str, Any]]:
        """
        관리자: ID로 특정 피드의 상세 정보를 조회 (기관/카테고리 이름 포함)
        """
        stmt = (
            select(
                Feed,
                Organization.name.label("organization_name"),
                Category.name.label("category_name")
            )
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
            .where(Feed.id == feed_id)
        )
        result = await self.db.execute(stmt)
        row = result.first()
        if row:
            feed_obj = row[0] # Feed ORM 객체
            # ORM 객체를 딕셔너리로 변환하고, JOIN된 이름들을 추가
            feed_dict = {c.name: getattr(feed_obj, c.name) for c in feed_obj.__table__.columns}
            feed_dict["organization_name"] = row.organization_name
            feed_dict["category_name"] = row.category_name
            return feed_dict
        return None

    async def update_feed(self, feed_id: int, update_data: Dict[str, Any]) -> bool:
        """
        관리자: 특정 피드의 정보를 수정
        """
        try:
            stmt = (
                update(Feed)
                .where(Feed.id == feed_id)
                .values(**update_data)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            # affected_rows가 0보다 크면 업데이트 성공
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating feed {feed_id}: {e}", exc_info=True)
            return False
        
    async def create_initial_feed(self, initial_data: Dict[str, Any]) -> Feed:
        """
        피드 생성 요청 시, 처리에 필요한 기본 정보만으로 피드 레코드를 먼저 생성
        processing_status는 기본값인 'processing'으로 설정

        Args:
            initial_data (Dict[str, Any]): title, organization_id 등 초기 데이터

        Returns:
            Feed: 생성된 Feed ORM 객체 (ID 포함)
        """
        new_feed = Feed(**initial_data)
        self.db.add(new_feed)
        await self.db.commit()
        await self.db.refresh(new_feed)
        return new_feed

    async def update_feed_after_processing(
        self,
        feed_id: int,
        summary: str,
        file_path: Optional[str],
        status: ProcessingStatusEnum
    ) -> bool:
        """
        백그라운드 처리 완료 후, 피드 정보를 최종 업데이트

        Args:
            feed_id (int): 업데이트할 피드의 ID
            summary (str): 생성된 요약문
            file_path (Optional[str]): 저장된 파일 경로 (PDF인 경우)
            status (ProcessingStatusEnum): 최종 처리 상태 ('completed' 또는 'failed')

        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            update_values = {
                "summary": summary,
                "processing_status": status
            }
            if file_path:
                update_values["pdf_file_path"] = file_path

            stmt = (
                update(Feed)
                .where(Feed.id == feed_id)
                .values(**update_values)
            )
            result = await self.db.execute(stmt)
            await self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating feed after processing for feed_id {feed_id}: {e}", exc_info=True)
            return False
        
    async def get_deactivated_feeds_list(
        self,
        page: int,
        limit: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        관리자 페이지: 비활성화된 피드 목록을 페이지네이션하여 조회
        """
        offset = (page - 1) * limit
        
        # is_active = False 조건만 다름
        base_query = (
            select(
                Feed.id,
                Feed.title,
                Organization.name.label("organization_name"),
                Category.name.label("category_name"),
                Feed.updated_at.label("deactivated_at") # is_active가 False로 변경된 시점
            )
            .join(Organization, Feed.organization_id == Organization.id)
            .join(Category, Feed.category_id == Category.id)
            .where(Feed.is_active == False)
        )

        count_stmt = select(func.count()).select_from(base_query.alias())
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar_one()

        data_stmt = base_query.order_by(Feed.updated_at.desc()).offset(offset).limit(limit)
        data_result = await self.db.execute(data_stmt)
        feeds = data_result.mappings().all()

        return list(feeds), total_count
    
    async def delete_feed_permanently(self, feed_id: int) -> bool:
        """
        관리자: 특정 피드를 데이터베이스에서 완전히 삭제
        Feed 모델의 cascade 설정에 따라 연관된 bookmarks, ratings도 함께 삭제
        """
        try:
            # 먼저 삭제할 피드 객체를 가져옵니다 (파일 경로 확인을 위해).
            feed_to_delete = await self.db.get(Feed, feed_id)
            if not feed_to_delete:
                return False # 삭제할 대상이 없음

            # 실제 파일 경로를 반환값으로 전달하기 위해 저장
            pdf_path_to_delete = feed_to_delete.pdf_file_path

            await self.db.delete(feed_to_delete)
            await self.db.commit()
            
            # 서비스 레이어에 삭제할 파일 경로를 반환
            return pdf_path_to_delete
        
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting feed {feed_id} permanently: {e}", exc_info=True)
            return False