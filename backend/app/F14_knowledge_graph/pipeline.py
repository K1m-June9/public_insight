import asyncio
import logging
import os
import fitz
import re
from elasticsearch import Elasticsearch
from typing import Dict, List, Any, Tuple

# --- 데이터 융합을 위한 작업 ---
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from kiwipiepy import Kiwi

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

# --- Kiwi 형태소 분석기 전역 인스턴스 생성 ---
# 모델을 로드하는 데 시간이 걸리므로, 스크립트 시작 시 한 번만 생성하여 재사용함.
kiwi = Kiwi()

# --- 데이터 구조 정의 (Type Hinting) ---
MysqlData = Dict[str, List[Dict[str, Any]]]
PdfTextData = Dict[int, str]
SearchLogData = List[Tuple[str, str]]
TransformedData = Tuple[List[Dict[str, Any]], List[Dict[str, Any]]] # (nodes, relationships)

# --- 형태소 분석기(일단 한국어 전용이라는데 기타 설정 등은 안한 상태) ---
def kiwi_tokenizer(text: str) -> List[str]:
    """
    (Tokenizer) Kiwi 형태소 분석기를 사용하여 텍스트에서 명사만 추출하는 함수.
    - TfidfVectorizer의 tokenizer로 사용될 것임.
    """
    # 1. kiwi.tokenize()를 사용하여 형태소 분석 수행
    tokens = kiwi.tokenize(text)
    # 2. 품사가 '일반 명사(NNG)' 또는 '고유 명사(NNP)'인 토큰만 추출함.
    # 3. 추가적으로, 한 글자짜리 명사는 의미 없는 경우가 많아 제외함 (예: '것', '수', '등').
    return [
        token.form for token in tokens 
        if token.tag in {'NNG', 'NNP'} and len(token.form) > 1
    ]


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

# =================================== EXTRACT ===================================
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
    (Helper) Elasticsearch에서 최근 1주일간의 사용자 검색 로그를 추출함.
    - 로그인/비로그인 사용자의 모든 검색 로그를 대상으로 함.
    """
    logger.info("Elasticsearch 연결 및 검색 로그 추출 시작...")
    
    try:
        es_client = Elasticsearch(
            "http://elasticsearch:9200",
            basic_auth=(settings.ELASTIC_USERNAME, settings.ELASTIC_PASSWORD)
        )
        if not es_client.ping():
            raise ConnectionError("Elasticsearch에 연결할 수 없음.")
    except Exception as e:
        logger.error(f"Elasticsearch 클라이언트 생성 실패: {e}")
        return []

    # --- 🔧 [수정] 더 명확하고 안전한 Query DSL ---
    # "지난 7일 동안, 백엔드 컨테이너에서 남긴, 정확히 검색 API 경로인 로그"
    query = {
        "query": {
            "bool": {
                "must": [
                    # 조건 1: 컨테이너 이름이 'backend'
                    {"match": {"container.name.keyword": "backend"}},
                    # 🔧 조건 2: URL 경로가 정확히 '/api/v1/search'
                    {"match": {"json.url.path": "/api/v1/search"}}
                ],
                "filter": [
                    # 조건 3: 시간 범위는 최근 7일
                    {"range": {"@timestamp": {"gte": "now-7d/d", "lt": "now/d"}}}
                ]
            }
        },
        "size": 10000,
        # 🔧 필요한 필드에 'json.url.query'도 명시적으로 추가
        "_source": ["json.user.id", "json.url.query", "message"], 
        "sort": [{"@timestamp": {"order": "desc"}}]
    }

    extracted_logs = []
    try:
        response = es_client.search(index="filebeat*", body=query)
        
        for hit in response['hits']['hits']:
            source = hit.get('_source', {})
            # 🔧 json 구조가 message 필드 안에 문자열로 있을 경우를 대비해 이중으로 파싱
            json_message = source.get('json')
            if not json_message and 'message' in source:
                try: # message 필드가 json 형태일 경우 파싱 시도
                    import json
                    json_message = json.loads(source['message'])
                except json.JSONDecodeError:
                    continue # json 파싱 실패 시 건너뜀

            if not json_message:
                continue

            # 이제 json_message 에서 안전하게 데이터 추출
            user_id = json_message.get('user', {}).get('id', 'anonymous') # ID가 없으면 'anonymous'
            query_string = json_message.get('url', {}).get('query')

            if not query_string:
                continue

            match = re.search(r'keyword=([^&]+)', query_string)
            if match:
                keyword = match.group(1)
                keyword = re.sub(r'%[0-9a-fA-F]{2}', lambda m: chr(int(m.group(0)[1:], 16)), keyword)
                
                # user_id가 있든 없든(anonymous) 모두 결과에 포함시킴
                extracted_logs.append((str(user_id), keyword))

    except Exception as e:
        logger.error(f"Elasticsearch 로그 검색 중 오류 발생: {e}", exc_info=True)
        return []

    return extracted_logs


# =================================== TRANSFORM ===================================
def phase_transform(
    mysql_data: MysqlData, 
    pdf_texts: PdfTextData, 
    search_logs: SearchLogData
) -> TransformedData:
    """
    ETL 파이프라인 2단계: Transform
    - 추출된 원본 데이터를 '지식 그래프'로 변환하는 핵심 로직.
    - 텍스트 통합, 키워드 추출, 유사도 계산 등을 수행함.
    """
    logger.info("--- Phase 2: Transform 시작 ---")

    # 1. 재료 준비: 모든 텍스트 소스를 피드별로 통합
    logger.info("1/4: 피드별 텍스트 통합 중...")
    all_feed_texts, feed_map = _unify_text_sources(mysql_data, pdf_texts)

    # 2. 맛의 핵심 추출: 형태소 분석 및 TF-IDF 벡터화
    logger.info("2/4: 키워드 추출 및 벡터화 진행 중...")
    tfidf_matrix, vectorizer = _vectorize_texts(all_feed_texts.values())

    # 3. 요리의 어울림 분석: 코사인 유사도 계산
    logger.info("3/4: 피드 간 코사인 유사도 계산 중...")
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # 4. 최종 플레이팅: 노드 및 관계 데이터 구조화
    logger.info("4/4: 최종 노드 및 관계 데이터 구조화 중...")
    nodes_to_create, relationships_to_create = _structure_graph_data(
        mysql_data, search_logs, feed_map, vectorizer, tfidf_matrix, similarity_matrix
    )
    
    logger.info(f"변환 완료: {len(nodes_to_create)}개의 노드, {len(relationships_to_create)}개의 관계 생성됨.")
    logger.info("--- Phase 2: Transform 종료 ---")
    
    return nodes_to_create, relationships_to_create


def _unify_text_sources(mysql_data: MysqlData, pdf_texts: PdfTextData) -> Tuple[Dict[int, str], Dict[int, Any]]:
    """
    (Helper) 각 피드의 모든 텍스트 소스(title, summary, original_text, pdf_text)를 하나로 합침.
    - NLP 분석의 입력으로 사용될 단일 '문서'를 생성하는 것이 목표임.
    - 반환값: ( {feed_id: "전체 텍스트"}, {feed_id: feed_객체} )
    """
    logger.info("  - unifying text sources for each feed...")
    
    # feed_id를 키로 사용하여 피드 객체에 빠르게 접근하기 위한 딕셔너리 생성
    feed_map = {feed['id']: feed for feed in mysql_data.get('feeds', [])}
    
    # {feed_id: "통합된 전체 텍스트"} 형태의 딕셔너리 생성
    all_feed_texts = {}

    for feed_id, feed in feed_map.items():
        # 1. 기본 텍스트: 제목(title)과 요약문(summary)은 항상 포함
        #    - None 값일 경우를 대비해 빈 문자열('')로 처리
        title = feed.get('title', '') or ''
        summary = feed.get('summary', '') or ''
        
        # 각 텍스트 요소를 줄바꿈 문자로 명확하게 분리하여 결합
        full_text_parts = [title, summary]

        # 2. 콘텐츠 타입에 따라 원문(본문) 추가
        content_type = feed.get('content_type')
        
        if content_type == 'text':
            # content_type이 'text'인 경우, original_text 컬럼의 값을 추가
            original_text = feed.get('original_text', '') or ''
            full_text_parts.append(original_text)
            
        elif content_type == 'pdf':
            # content_type이 'pdf'인 경우, Extract 단계에서 추출한 PDF 텍스트를 추가
            # pdf_texts 딕셔너리에서 해당 feed_id의 텍스트를 찾아옴
            pdf_content = pdf_texts.get(feed_id, '') or ''
            full_text_parts.append(pdf_content)
        
        # 3. 모든 텍스트 조각을 하나의 긴 문자열로 결합
        all_feed_texts[feed_id] = "\n".join(filter(None, full_text_parts))

    return all_feed_texts, feed_map


def _vectorize_texts(texts: List[str]) -> Tuple[Any, TfidfVectorizer]:
    """
    (Helper) 통합된 텍스트 모음을 TF-IDF 행렬로 변환함.
    - 내부적으로 kiwi_tokenizer를 사용하여 한국어 텍스트를 처리함.
    - 반환값: (TF-IDF 행렬, 학습된 Vectorizer 객체)
    """
    logger.info("  - TF-IDF Vectorizer 생성 및 학습 시작...")

    # TfidfVectorizer 객체 생성.
    # 이 객체가 NLP의 핵심적인 연산을 수행함.
    vectorizer = TfidfVectorizer(
        # tokenizer: 텍스트를 어떤 단위(토큰)로 쪼갤지 결정하는 함수.
        #           우리가 만든 kiwi_tokenizer를 지정하여 한국어 명사 기반으로 작동하게 함.
        tokenizer=kiwi_tokenizer,
        
        # max_df: "Document Frequency"의 최대값 (0.0 ~ 1.0 사이).
        #         너무 많은 문서(예: 전체의 85% 이상)에 공통으로 나타나는 단어는
        #         분석에서 제외함. '그리고', '하지만' 등과 같은 불용어(stopword)일
        #         가능성이 높기 때문임.
        max_df=0.85,
        
        # min_df: "Document Frequency"의 최소값 (정수).
        #         너무 적은 수의 문서(예: 2개 미만)에만 나타나는 단어는
        #         무시함. 오탈자이거나 분석에 큰 의미가 없는 단어일
        #         가능성이 높기 때문임.
        min_df=2,

        # ngram_range: 함께 고려할 단어의 범위. (min, max) 튜플.
        #              (1, 2)는 '부동산' 같은 단일 단어(1-gram) 뿐만 아니라,
        #              '부동산 정책' 같은 연속된 두 단어(2-gram)도 하나의
        #              키워드로 함께 고려함. 키워드의 의미를 훨씬 풍부하게 만들어 줌.
        ngram_range=(1, 2)
    )

    # .fit_transform(): 텍스트 데이터에 벡터라이저를 학습(fit)시키고,
    #                  그 결과로 텍스트를 TF-IDF 행렬로 변환(transform)함.
    # 이 과정이 가장 많은 연산량을 요구하는 부분임.
    tfidf_matrix = vectorizer.fit_transform(texts)
    
    logger.info(f"  - TF-IDF 행렬 생성 완료. (크기: {tfidf_matrix.shape})")

    # 다음 단계(유사도 계산, 키워드 추출)에서 사용하기 위해
    # 변환된 행렬과 학습이 완료된 벡터라이저 객체를 모두 반환함.
    return tfidf_matrix, vectorizer


def _get_top_keywords(tfidf_vector, vectorizer, top_n=10) -> List[Tuple[str, float]]:
    """(Sub-Helper) 특정 문서의 TF-IDF 벡터에서 상위 N개의 키워드와 점수를 추출함."""
    # 벡터를 NumPy 배열로 변환
    flat_vector = tfidf_vector.toarray().flatten()
    # TF-IDF 점수가 높은 순으로 인덱스를 정렬
    top_indices = np.argsort(flat_vector)[-top_n:][::-1]
    
    feature_names = vectorizer.get_feature_names_out()
    
    keywords = []
    for i in top_indices:
        # 점수가 0인 경우는 키워드로 추가하지 않음
        if flat_vector[i] > 0:
            keywords.append((feature_names[i], round(float(flat_vector[i]), 4)))
            
    return keywords


def _structure_graph_data(
    mysql_data: MysqlData, 
    search_logs: SearchLogData,
    feed_map: Dict[int, Any],
    vectorizer: TfidfVectorizer, 
    tfidf_matrix, #稀疏矩阵
    similarity_matrix, #密集矩阵
    similarity_threshold: float = 0.2 # 유사도 임계값
) -> TransformedData:
    """
    (Helper) 모든 분석 결과를 Neo4j에 적재할 최종 형태로 구조화함.
    - 이 함수는 ETL의 'Transform' 단계의 최종 조립 라인임.
    """
    nodes = []
    relationships = []

    # --- 1. MySQL 데이터 기반 노드 및 관계 생성 ---
    logger.info("    - 1/4: MySQL 데이터 기반 노드/관계 구조화...")
    nodes.extend([{'label': 'User', **user} for user in mysql_data['users']])
    nodes.extend([{'label': 'Organization', **org} for org in mysql_data['organizations']])
    nodes.extend([{'label': 'Category', **cat} for cat in mysql_data['categories']])
    nodes.extend([{'label': 'Feed', **feed} for feed in mysql_data['feeds']])

    # RATED 관계 (점수별로 세분화)
    for rating in mysql_data['ratings']:
        score = rating['score']
        if score >= 4: rel_type = 'RATED_POSITIVELY'
        elif score == 3: rel_type = 'RATED_NORMALLY'
        else: rel_type = 'RATED_NEGATIVELY'
        relationships.append({
            'start_node': ('User', rating['user_id']),
            'end_node': ('Feed', rating['feed_id']),
            'type': rel_type,
            'properties': {'score': score}
        })
    # 기타 MySQL 기반 관계
    relationships.extend([
        {'start_node': ('User', bm['user_id']), 'end_node': ('Feed', bm['feed_id']), 'type': 'BOOKMARKED'}
        for bm in mysql_data['bookmarks']
    ])
    relationships.extend([
        {'start_node': ('Organization', feed['organization_id']), 'end_node': ('Feed', feed['id']), 'type': 'PUBLISHED'}
        for feed in mysql_data['feeds']
    ])
    relationships.extend([
        {'start_node': ('Feed', feed['id']), 'end_node': ('Category', feed['category_id']), 'type': 'BELONGS_TO'}
        for feed in mysql_data['feeds']
    ])

    # --- 2. NLP 분석 기반 키워드 노드 및 관계 생성 ---
    logger.info("    - 2/4: NLP 기반 키워드 노드/관계 구조화...")
    # vectorizer의 단어 사전 자체가 Keyword 노드의 후보가 됨
    all_keywords = vectorizer.get_feature_names_out()
    nodes.extend([{'label': 'Keyword', 'id': keyword, 'name': keyword} for keyword in all_keywords])
    
    feed_ids = list(feed_map.keys())
    for i, feed_id in enumerate(feed_ids):
        # 각 피드(문서)의 TF-IDF 벡터에서 상위 10개 키워드를 추출
        top_keywords = _get_top_keywords(tfidf_matrix[i], vectorizer, top_n=10)
        for keyword, score in top_keywords:
            relationships.append({
                'start_node': ('Feed', feed_id),
                'end_node': ('Keyword', keyword),
                'type': 'CONTAINS_KEYWORD',
                'properties': {'score': score}
            })

    # --- 3. NLP 분석 기반 유사도 관계 생성 ---
    logger.info("    - 3/4: NLP 기반 유사도 관계 구조화...")
    # similarity_matrix는 자기 자신과의 비교도 포함하므로, 중복을 피하기 위해 상단 삼각형 부분만 순회
    for i in range(len(feed_ids)):
        for j in range(i + 1, len(feed_ids)):
            score = similarity_matrix[i, j]
            if score >= similarity_threshold:
                relationships.append({
                    'start_node': ('Feed', feed_ids[i]),
                    'end_node': ('Feed', feed_ids[j]),
                    'type': 'IS_SIMILAR_TO',
                    'properties': {'score': round(float(score), 4)}
                })

    # --- 4. Elasticsearch 로그 기반 검색 관계 생성 ---
    logger.info("    - 4/4: 검색 로그 기반 관계 구조화...")
    for user_id, keyword in search_logs:
        # 검색된 키워드가 우리 단어 사전에 있는 경우에만 관계를 생성
        if keyword in all_keywords:
            start_node_label = 'User' if user_id != 'anonymous' else 'AnonymousUser'
            # (AnonymousUser 노드를 위한 처리 - 지금은 User와 동일하게 처리하되, ID만 다름)
            if start_node_label == 'AnonymousUser':
                # 익명 사용자 노드가 없다면 추가 (단 한번만)
                if not any(n['label'] == 'AnonymousUser' for n in nodes):
                    nodes.append({'label': 'AnonymousUser', 'id': 'anonymous', 'name': 'Anonymous User'})
            
            relationships.append({
                'start_node': (start_node_label, user_id),
                'end_node': ('Keyword', keyword),
                'type': 'SEARCHED'
            })

    return nodes, relationships


# =================================== LOAD ===================================
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