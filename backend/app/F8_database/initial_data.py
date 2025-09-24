# app/F8_database/initial_data.py
import logging
from sqlalchemy import select, func, insert
from sqlalchemy.ext.asyncio import AsyncSession

# 필요한 모델들을 import
from app.F7_models.organizations import Organization
from app.F7_models.categories import Category

logger = logging.getLogger(__name__)

async def seed_initial_data(db: AsyncSession):
    """
    애플리케이션 시작 시, 필요한 초기 데이터(기관, 카테고리 등)가 없으면 생성합니다.
    """
    # 1. organizations 테이블이 비어있는지 먼저 확인
    #    하나라도 데이터가 있으면, 전체 시딩 과정을 건너뜁니다.
    check_stmt = select(func.count()).select_from(Organization)
    result = await db.execute(check_stmt)
    if result.scalar_one() > 0:
        logger.info("Initial data for organizations and categories already exists. Skipping seeding.")
        return

    try:
        logger.info("Seeding initial data for organizations and categories...")
        
        # 2. 초기 기관 데이터 정의
        initial_orgs = [
            {'id': 219, 'name': '국회', 'description': '국회', 'website_url': 'https://www.assembly.go.kr/portal/main/main.do', 'icon_path': '7cc60336-8133-4cef-8c28-37a87e2ec55f.ico', 'is_active': True},
            {'id': 220, 'name': '교육부', 'description': '교육부', 'website_url': 'https://www.moe.go.kr/', 'icon_path': 'a22f3547-dbac-4d42-bc7b-9afc8b7dd095.ico', 'is_active': True},
            {'id': 221, 'name': '고용노동부', 'description': '고용노동부', 'website_url': 'https://www.moel.go.kr/index.do', 'icon_path': '0287f415-b6fc-4e27-b7c9-b39efebebdc2.ico', 'is_active': True},
            {'id': 222, 'name': '문화체육관광부', 'description': '문화체육관광부', 'website_url': 'https://www.mcst.go.kr/kor/main.jsp', 'icon_path': '2c2854be-1f25-4e89-b9ef-a0b976457aa8.ico', 'is_active': True},
            {'id': 223, 'name': '여성가족부', 'description': '여성가족부', 'website_url': 'https://www.mogef.go.kr/', 'icon_path': '965d9d72-622d-4dc3-b37b-592fa6c8dece.ico', 'is_active': True},
        ]
        # SQLAlchemy Core의 insert()를 사용하여 bulk insert 실행
        await db.execute(insert(Organization).values(initial_orgs))
        logger.info(f"Seeded {len(initial_orgs)} organizations.")

        # 3. 초기 카테고리 데이터 정의
        initial_cats = [
            # 고용노동부 (org_id: 221)
            {'id': 109, 'organization_id': 221, 'name': '건설산재예방정책과', 'is_active': True},
            {'id': 110, 'organization_id': 221, 'name': '고령사회인력정책과', 'is_active': True},
            {'id': 111, 'organization_id': 221, 'name': '고용문화개선정책과', 'is_active': True},
            {'id': 112, 'organization_id': 221, 'name': '고용차별개선과', 'is_active': True},
            {'id': 113, 'organization_id': 221, 'name': '고용채용기반과', 'is_active': True},
            {'id': 114, 'organization_id': 221, 'name': '국민취업지원기획팀', 'is_active': True},
            {'id': 115, 'organization_id': 221, 'name': '근로기준정책과', 'is_active': True},
            {'id': 116, 'organization_id': 221, 'name': '기업일자리지원과', 'is_active': True},
            {'id': 117, 'organization_id': 221, 'name': '기획재정담당관', 'is_active': True},
            {'id': 118, 'organization_id': 221, 'name': '산재예방지원과', 'is_active': True},
            {'id': 119, 'organization_id': 221, 'name': '안전문화협력팀', 'is_active': True},
            {'id': 120, 'organization_id': 221, 'name': '여성고용정책과', 'is_active': True},
            {'id': 121, 'organization_id': 221, 'name': '일가정양립추진단', 'is_active': True},
            {'id': 122, 'organization_id': 221, 'name': '중대산업재해감독과', 'is_active': True},
            {'id': 123, 'organization_id': 221, 'name': '지역산업고용정책과', 'is_active': True},
            {'id': 124, 'organization_id': 221, 'name': '직업건강증진팀', 'is_active': True},
            {'id': 125, 'organization_id': 221, 'name': '퇴직연금복지과', 'is_active': True},
            {'id': 126, 'organization_id': 221, 'name': '혁신행정담당관', 'is_active': True},
            {'id': 127, 'organization_id': 221, 'name': '화학사고예방과', 'is_active': True},
            {'id': 157, 'organization_id': 221, 'name': '보도자료', 'is_active': True},
            {'id': 160, 'organization_id': 221, 'name': '정책뉴스', 'is_active': True},

            # 교육부 (org_id: 220)
            {'id': 128, 'organization_id': 220, 'name': '교원', 'is_active': True},
            {'id': 129, 'organization_id': 220, 'name': '교육발전특구', 'is_active': True},
            {'id': 130, 'organization_id': 220, 'name': '교육통계 및 정보화', 'is_active': True},
            {'id': 131, 'organization_id': 220, 'name': '국외(유학) 교육', 'is_active': True},
            {'id': 132, 'organization_id': 220, 'name': '대학(원) 교육', 'is_active': True},
            {'id': 133, 'organization_id': 220, 'name': '영유아 보육 교육', 'is_active': True},
            {'id': 134, 'organization_id': 220, 'name': '지방교육자치', 'is_active': True},
            {'id': 135, 'organization_id': 220, 'name': '초등돌봄교육', 'is_active': True},
            {'id': 136, 'organization_id': 220, 'name': '초중고 교육', 'is_active': True},
            {'id': 137, 'organization_id': 220, 'name': '평생교육', 'is_active': True},
            {'id': 138, 'organization_id': 220, 'name': 'RISE글로컬대학', 'is_active': True},
            {'id': 158, 'organization_id': 220, 'name': '보도자료', 'is_active': True},
            {'id': 161, 'organization_id': 220, 'name': '정책뉴스', 'is_active': True},

            # 국회 (org_id: 219)
            {'id': 139, 'organization_id': 219, 'name': '국회의원정책자료', 'is_active': True},
            {'id': 140, 'organization_id': 219, 'name': '법제정보', 'is_active': True},
            {'id': 141, 'organization_id': 219, 'name': '정책연구보고서', 'is_active': True},
            {'id': 159, 'organization_id': 219, 'name': '보도자료', 'is_active': True},
            {'id': 162, 'organization_id': 219, 'name': '정책뉴스', 'is_active': True},

            # 문화체육관광부 (org_id: 222)
            {'id': 142, 'organization_id': 222, 'name': '관광', 'is_active': True},
            {'id': 143, 'organization_id': 222, 'name': '국민소통', 'is_active': True},
            {'id': 144, 'organization_id': 222, 'name': '국제문화홍보', 'is_active': True},
            {'id': 145, 'organization_id': 222, 'name': '기획조정지원', 'is_active': True},
            {'id': 146, 'organization_id': 222, 'name': '문화예술', 'is_active': True},
            {'id': 147, 'organization_id': 222, 'name': '종무', 'is_active': True},
            {'id': 148, 'organization_id': 222, 'name': '체육', 'is_active': True},
            {'id': 149, 'organization_id': 222, 'name': '콘텐츠저작권미디어', 'is_active': True},
            {'id': 156, 'organization_id': 222, 'name': '보도자료', 'is_active': True},
            {'id': 163, 'organization_id': 222, 'name': '정책뉴스', 'is_active': True},

            # 여성가족부 (org_id: 223)
            {'id': 150, 'organization_id': 223, 'name': '가족', 'is_active': True},
            {'id': 151, 'organization_id': 223, 'name': '기타정책', 'is_active': True},
            {'id': 152, 'organization_id': 223, 'name': '양성평등', 'is_active': True},
            {'id': 153, 'organization_id': 223, 'name': '인권보호', 'is_active': True},
            {'id': 154, 'organization_id': 223, 'name': '청소년', 'is_active': True},
            {'id': 155, 'organization_id': 223, 'name': '보도자료', 'is_active': True},
            {'id': 164, 'organization_id': 223, 'name': '정책뉴스', 'is_active': True},
        ]
        await db.execute(insert(Category).values(initial_cats))
        logger.info(f"Seeded {len(initial_cats)} categories.")
        
        # 4. 모든 작업이 성공적으로 끝나면 커밋
        await db.commit()
        logger.info("Initial data seeding committed successfully.")

    except Exception as e:
        logger.error(f"An error occurred during data seeding: {e}", exc_info=True)
        # 에러 발생 시, 롤백하여 데이터 일관성 유지
        await db.rollback()