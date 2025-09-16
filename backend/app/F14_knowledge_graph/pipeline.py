import asyncio
import logging
import os
import fitz
from typing import Dict, List, Any, Tuple

# --- SQLAlchemy 비동기 설정 ---
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# --- 프로젝트 모델 임포트 ---
# (settings와 모델 경로는 실제 프로젝트 구조에 맞게 조정 필요)
from app.F5_core.config import settings
from app.F7_models.users import User
from app.F7_models.organizations import Organization
from app.F7_models.categories import Category
from app.F7_models.feeds import Feed
from app.F7_models.bookmarks import Bookmark
from app.F7_models.ratings import Rating

# --- 로깅 설정 ---
logger = logging.getLogger(__name__)


# --- 데이터 구조 정의 (Type Hinting) ---
MysqlData = Dict[str, List[Dict[str, Any]]]
PdfTextData = Dict[int, str]
SearchLogData = List[Tuple[str, str]]


# ---------- 스크립트 실행 위치에 상관없이 항상 올바른 경로를 찾도록 초기에 설정 ----------
# 1. 현재 이 파일(pipeline.py)의 절대 경로를 찾음
#    ex: /home/pumpkinbee/public_insight/app/F14_knowledge_graph/pipeline.py
current_file_path = os.path.abspath(__file__)

# 2. F14_knowledge_graph 폴더의 경로를 찾음 (한 단계 위)
#    ex: /home/pumpkinbee/public_insight/app/F14_knowledge_graph
f14_dir = os.path.dirname(current_file_path)

# 3. app 폴더의 경로를 찾음 (두 단계 위)
#    ex: /home/pumpkinbee/public_insight/app
app_dir = os.path.dirname(f14_dir)

# 4. 프로젝트 루트 경로를 찾음 (세 단계 위)
#    ex: /home/pumpkinbee/public_insight
project_root_dir = os.path.dirname(app_dir)

# 5. 루트 경로를 기준으로 static 폴더의 절대 경로를 생성함
#    이렇게 하면 이 스크립트를 어디서 실행하든 항상 동일한 절대 경로를 가리킴
PDF_BASE_PATH = os.path.join(project_root_dir, "backend", "static", "feeds_pdf")

# --- MySQL 연결 설정 (개발/테스트용) ---
DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}:{settings.DB_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def phase_extract(db: AsyncSession) -> Tuple[MysqlData, PdfTextData, SearchLogData]:
    """
    ETL 파이프라인 1단계: Extract
    - 여러 데이터 소스(MySQL, PDF, Elasticsearch)에서 원본 데이터 추출함.
    - 데이터 가공 없이, 있는 그대로 가져오는 것에 집중함.
    """
    logger.info("--- Phase 1: Extract 시작 ---")

    # 1.1: MySQL에서 데이터 추출
    mysql_data = await _extract_from_mysql(db)
    feed_count = len(mysql_data.get('feeds', []))
    logger.info(f"MySQL에서 {feed_count}개의 피드 포함, 전체 데이터 추출 완료.")

    # 1.2: PDF 파일에서 텍스트 추출
    # 🔧 수정: content_type이 'PDF'인 피드만 필터링하여 전달함
    feeds_with_pdf = [
        f for f in mysql_data.get('feeds', []) 
        if f.get('content_type') == 'pdf' and f.get('pdf_file_path')
    ]
    pdf_texts = _extract_text_from_pdfs(feeds_with_pdf)
    logger.info(f"{len(pdf_texts)}개의 PDF 파일에서 텍스트 추출 완료.")
    
    # 1.3: Elasticsearch에서 검색 로그 추출
    search_logs = _extract_search_logs_from_es()
    logger.info(f"Elasticsearch에서 {len(search_logs)}개의 검색 로그 추출 완료.")

    logger.info("--- Phase 1: Extract 종료 ---")
    
    return mysql_data, pdf_texts, search_logs


async def _extract_from_mysql(db: AsyncSession) -> MysqlData:
    """
    (Helper) SQLAlchemy를 사용하여 MySQL의 6개 핵심 테이블에서 데이터를 가져옴.
    - Feed 테이블에서 content_type과 original_text를 추가로 조회함.
    """
    user_res = await db.execute(select(User.id, User.user_id, User.nickname))
    org_res = await db.execute(select(Organization.id, Organization.name))
    cat_res = await db.execute(select(Category.id, Category.name, Category.organization_id))
    
    # 🔧 수정: Feed 테이블 조회 시 content_type과 original_text 컬럼 추가
    feed_res = await db.execute(select(
        Feed.id, Feed.title, Feed.summary, 
        Feed.content_type, Feed.pdf_file_path, Feed.original_text,
        Feed.organization_id, Feed.category_id, Feed.published_date
    ))
    
    bookmark_res = await db.execute(select(Bookmark.user_id, Bookmark.feed_id))
    rating_res = await db.execute(select(Rating.user_id, Rating.feed_id, Rating.score))

    data = {
        "users": [dict(r) for r in user_res.mappings().all()],
        "organizations": [dict(r) for r in org_res.mappings().all()],
        "categories": [dict(r) for r in cat_res.mappings().all()],
        "feeds": [dict(r) for r in feed_res.mappings().all()],
        "bookmarks": [dict(r) for r in bookmark_res.mappings().all()],
        "ratings": [dict(r) for r in rating_res.mappings().all()],
    }
    return data


def _extract_text_from_pdfs(feeds: List[Dict[str, Any]]) -> PdfTextData:
    """
    (Helper) PyMuPDF (fitz)를 사용하여 PDF 파일 목록에서 텍스트를 추출함.
    - 각 피드의 'pdf_file_path'를 기반으로 실제 파일 경로를 구성하고 텍스트를 읽음.
    - 파일이 없거나 오류 발생 시, 해당 피드는 건너뛰고 로그를 남김.
    """
    # 💥 중요: 이 경로는 스크립트가 실행되는 위치를 기준으로 해야 함.
    # 보통 프로젝트의 루트 디렉토리임.
    base_path = PDF_BASE_PATH
    extracted_texts = {}

    for feed in feeds:
        feed_id = feed.get('id')
        relative_path = feed.get('pdf_file_path')

        if not feed_id or not relative_path:
            continue

        # UUID 파일명에 .pdf 확장자를 추가하여 전체 파일 경로 생성
        pdf_path = os.path.join(base_path, f"{relative_path}.pdf")

        try:
            # 파일 존재 여부 확인
            if not os.path.exists(pdf_path):
                logger.warning(f"PDF 파일 없음 (건너뜀): {pdf_path}")
                continue
            
            # PDF 파일을 열고 모든 페이지의 텍스트를 추출하여 결합함
            doc = fitz.open(pdf_path)
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            extracted_texts[feed_id] = full_text
            doc.close()

        except Exception as e:
            # PyMuPDF 처리 중 발생할 수 있는 모든 예외를 처리함
            logger.error(f"PDF 처리 오류 (건너뜀): {pdf_path} | 오류: {e}")
            continue
            
    return extracted_texts


def _extract_search_logs_from_es() -> SearchLogData:
    """
    (Helper) Elasticsearch Python 클라이언트를 사용하여 최근 검색 로그를 가져옴.
    """
    # TODO: Elasticsearch 쿼리를 사용하여 로그를 조회하는 로직 구현
    logger.info("TODO: Elasticsearch 검색 로그 추출 로직 구현")
    # 임시 데이터
    return [("1", "청년주택"), ("anonymous", "부동산 정책")]

# --- 다음 단계 함수 (뼈대) ---
def phase_transform(mysql_data: MysqlData, pdf_texts: PdfTextData, search_logs: SearchLogData):
    logger.info("--- Phase 2: Transform 시작 ---")
    pass

def phase_load():
    logger.info("--- Phase 3: Load 시작 ---")
    pass

# --- 메인 실행 함수 (개발/테스트용) ---
async def run_pipeline_for_dev():
    """
    개발 환경에서 파이프라인을 단독으로 실행하기 위한 비동기 함수.
    - 실제 스케줄러가 이와 유사한 방식으로 파이프라인을 호출할 것임.
    """
    logger.info("======= Knowledge Graph ETL Pipeline (DEV) 시작 =======")
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. Extract
            mysql_data, pdf_texts, search_logs = await phase_extract(db)
            
            # 2. Transform (아직 구현되지 않음)
            # transformed_data = phase_transform(mysql_data, pdf_texts, search_logs)
            
            # 3. Load (아직 구현되지 않음)
            # await phase_load(db, transformed_data)

        except Exception as e:
            logger.error(f"파이프라인 실행 중 오류 발생: {e}", exc_info=True)

    logger.info("======= Knowledge Graph ETL Pipeline (DEV) 종료 =======")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_pipeline_for_dev())