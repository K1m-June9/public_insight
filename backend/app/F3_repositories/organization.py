import logging

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from datetime import date

from app.F7_models.organizations import Organization
from app.F7_models.categories import Category
from app.F7_models.feeds import Feed
from app.F7_models.word_clouds import WordCloud

logger = logging.getLogger(__name__)

class OrganizationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # 활성화된 기관 목록과 각 기관별 피드 개수 조회 메서드
    # 입력: 없음
    # 반환: 
    #   기관 정보와 피드 개수가 포함된 딕셔너리 리스트
    #   [{"organization_id": int, "organization_name": str, "feed_count": int}, ...]
    # 설명: 
    #   활성화된 기관(is_active=True)과 해당 기관의 활성화된 피드 개수를 집계하여 반환
    #   LEFT JOIN을 사용하여 피드가 없는 기관도 포함 (feed_count=0으로 표시)
    #   기관 ID 오름차순으로 정렬하여 일관된 순서 보장
    #   성능 최적화를 위해 단일 쿼리로 모든 데이터 처리
    async def get_organizations_with_feed_counts(self) -> List[Dict[str, Any]]:
        # LEFT JOIN을 사용하여 기관과 피드를 연결하고 피드 개수 집계
        # 활성화된 기관만 조회하되, 피드가 없는 기관도 포함
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                func.count(Feed.id).label('feed_count')
            )
            .select_from(Organization)
            .outerjoin(
                Feed, 
                (Organization.id == Feed.organization_id) & (Feed.is_active == True)
            )
            .where(Organization.is_active == True)
            .group_by(Organization.id, Organization.name)
            .order_by(Organization.id.asc())
        )
        
        try:
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            # 결과를 딕셔너리 리스트로 변환
            organizations_data = []
            for row in rows:
                organizations_data.append({
                    "organization_id": row.organization_id,
                    "organization_name": row.organization_name,
                    "feed_count": row.feed_count
                })
            
            logger.info(f"활성화된 기관 {len(organizations_data)}개와 피드 개수 조회 완료")
            return organizations_data
            
        except Exception as e:
            logger.error(f"기관별 피드 개수 조회 중 오류 발생: {str(e)}")
            raise

    # 기관명으로 해당 기관의 카테고리 목록과 각 카테고리별 피드 개수 조회 메서드 ('보도자료' 제외)
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   기관 정보와 카테고리별 피드 개수가 포함된 딕셔너리 또는 None
    #   {"organization": {"id": int, "name": str}, "categories": [{"category_id": int, "category_name": str, "feed_count": int}, ...]}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하고, 해당 기관의 활성화된 카테고리와 각 카테고리별 활성화된 피드 개수를 집계
    #   '보도자료' 카테고리는 원형 그래프 구성에서 제외하므로 조회 대상에서 제외
    #   LEFT JOIN을 사용하여 피드가 없는 카테고리도 포함 (feed_count=0으로 표시)
    #   카테고리 ID 오름차순으로 정렬하여 일관된 순서 보장
    #   존재하지 않는 기관이거나 활성화된 카테고리가 없는 경우 None 반환
    async def get_categories_with_feed_counts_by_org_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        # 기관, 카테고리, 피드를 JOIN하여 카테고리별 피드 개수 집계
        # 기관명으로 조회하되 기관 활성화 상태는 확인하지 않음
        # 활성화된 카테고리 중 '보도자료'를 제외하고 활성화된 피드만 대상으로 함
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                Category.id.label('category_id'),
                Category.name.label('category_name'),
                func.count(Feed.id).label('feed_count')
            )
            .select_from(Organization)
            .join(Category, Organization.id == Category.organization_id)
            .outerjoin(
                Feed,
                (Category.id == Feed.category_id) & (Feed.is_active == True)
            )
            .where(
                Organization.name == org_name,
                Category.is_active == True,
                Category.name != '보도자료'  # '보도자료' 카테고리 제외
            )
            .group_by(
                Organization.id,
                Organization.name,
                Category.id,
                Category.name
            )
            .order_by(Category.id.asc())
        )
        
        try:
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            # 결과가 없는 경우 None 반환
            if not rows:
                logger.warning(f"기관 '{org_name}'에 대한 활성화된 카테고리를 찾을 수 없습니다 ('보도자료' 제외)")
                return None
            
            # 첫 번째 행에서 기관 정보 추출
            first_row = rows[0]
            organization_info = {
                "id": first_row.organization_id,
                "name": first_row.organization_name
            }
            
            # 카테고리별 피드 개수 데이터 구성
            categories_data = []
            total_feed_count = 0
            
            for row in rows:
                feed_count = row.feed_count
                total_feed_count += feed_count
                
                categories_data.append({
                    "category_id": row.category_id,
                    "category_name": row.category_name,
                    "feed_count": feed_count
                })
            
            # 모든 카테고리의 피드 개수가 0인 경우 None 반환
            if total_feed_count == 0:
                logger.warning(f"기관 '{org_name}'의 모든 카테고리에 활성화된 피드가 없습니다 ('보도자료' 제외)")
                return None
            
            result_data = {
                "organization": organization_info,
                "categories": categories_data
            }
            
            logger.info(f"기관 '{org_name}'의 카테고리 {len(categories_data)}개와 피드 개수 조회 완료 ('보도자료' 제외, 총 피드: {total_feed_count}개)")
            return result_data
            
        except Exception as e:
            logger.error(f"기관별 카테고리 피드 개수 조회 중 오류 발생: {str(e)}")
            raise

    # 기관명으로 기관 정보 조회 메서드 (아이콘 표시용)
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    # 반환: 
    #   기관 정보가 포함된 딕셔너리 또는 None
    #   {"id": int, "name": str, "website_url": str, "icon_path": str}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하여 아이콘 표시에 필요한 기본 정보 반환
    #   기관의 활성화 상태와 무관하게 조회 (name 조건만 사용)
    #   존재하지 않는 기관인 경우 None 반환하여 Service 레이어에서 처리
    #   Service 레이어에서 Base64 인코딩 및 스키마 변환에 활용
    async def get_organization_by_name(self, org_name: str) -> Optional[Dict[str, Any]]:
        # 기관명으로 기관 기본 정보 조회
        # 아이콘 표시에 필요한 필드만 선택하여 성능 최적화
        query = select(
            Organization.id,
            Organization.name,
            Organization.website_url,
            Organization.icon_path
        ).where(Organization.name == org_name)
        
        try:
            result = await self.db.execute(query)
            row = result.fetchone()
            
            # 결과가 없는 경우 None 반환
            if not row:
                logger.warning(f"기관 '{org_name}'을 찾을 수 없습니다")
                return None
            
            # 딕셔너리 형태로 변환하여 반환
            organization_data = {
                "id": row.id,
                "name": row.name,
                "website_url": row.website_url,
                "icon_path": row.icon_path
            }
            
            logger.info(f"기관 '{org_name}' 정보 조회 완료")
            return organization_data
            
        except Exception as e:
            logger.error(f"기관 '{org_name}' 정보 조회 중 오류 발생: {str(e)}")
            raise

    # 기관명으로 해당 기관의 최근 2개년 워드클라우드 데이터 조회 메서드
    # 입력: 
    #   org_name - 조회할 기관의 이름 (str)
    #   current_date - 현재 날짜 (date)
    # 반환: 
    #   기관 정보와 워드클라우드 데이터가 포함된 딕셔너리 또는 None
    #   {"organization": {"id": int, "name": str}, "wordclouds": [{"cloud_data": list, "period_start": date, "period_end": date, "created_at": datetime}, ...]}
    # 설명: 
    #   주어진 기관명으로 기관을 조회하고, 현재 날짜 기준 최근 2개년의 워드클라우드 데이터를 반환
    #   period_start의 연도를 기준으로 최근 2개년 필터링 (예: 2025년 → 2024, 2025년 데이터)
    #   생성일 기준 내림차순 정렬하여 최신 데이터 우선 반환
    #   존재하지 않는 기관이거나 워드클라우드 데이터가 없는 경우 None 반환
    async def get_organization_wordclouds_by_name(self, org_name: str, current_date: date) -> Optional[Dict[str, Any]]:
        # 현재 연도 기준 최근 2개년 계산
        current_year = current_date.year
        target_years = [current_year, current_year - 1]  # 예: [2025, 2024]
        
        # 기관과 워드클라우드를 JOIN하여 최근 2개년 데이터 조회
        # period_start의 연도를 기준으로 필터링
        query = (
            select(
                Organization.id.label('organization_id'),
                Organization.name.label('organization_name'),
                WordCloud.cloud_data,
                WordCloud.period_start,
                WordCloud.period_end,
                WordCloud.created_at
            )
            .select_from(Organization)
            .join(WordCloud, Organization.id == WordCloud.organization_id)
            .where(
                Organization.name == org_name,
                func.year(WordCloud.period_start).in_(target_years)
            )
            .order_by(WordCloud.created_at.desc())  # 최신 데이터 우선
        )
        
        try:
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            # 결과가 없는 경우 None 반환
            if not rows:
                logger.warning(f"기관 '{org_name}'의 최근 2개년 워드클라우드 데이터를 찾을 수 없습니다")
                return None
            
            # 첫 번째 행에서 기관 정보 추출
            first_row = rows[0]
            organization_info = {
                "id": first_row.organization_id,
                "name": first_row.organization_name
            }
            
            # 워드클라우드 데이터 구성
            wordclouds_data = []
            for row in rows:
                wordcloud_item = {
                    "cloud_data": row.cloud_data,  # JSON 데이터 그대로 반환
                    "period_start": row.period_start,
                    "period_end": row.period_end,
                    "created_at": row.created_at
                }
                wordclouds_data.append(wordcloud_item)
            
            result_data = {
                "organization": organization_info,
                "wordclouds": wordclouds_data
            }
            
            logger.info(f"기관 '{org_name}'의 워드클라우드 {len(wordclouds_data)}개 조회 완료 (대상 연도: {target_years})")
            return result_data
            
        except Exception as e:
            logger.error(f"기관 '{org_name}' 워드클라우드 조회 중 오류 발생: {str(e)}")
            raise