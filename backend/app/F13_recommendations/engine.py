import logging
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session # 서비스 레이어에서 동기 세션을 사용할 경우를 대비

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.F7_models.feeds import Feed
from app.F7_models.categories import Category

logger = logging.getLogger(__name__)

# '보도자료' 카테고리의 이름을 상수로 정의하여 코드의 명확성을 높입니다.
PRESS_RELEASE_CATEGORY_NAME = "보도자료"

class RecommendationEngine:
    """
    TF-IDF와 코사인 유사도를 기반으로 콘텐츠 기반 추천을 수행하는 엔진.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        self.tfidf_matrix = None
        self.feed_map: Dict[int, int] = {}
        # 이제 실제 Feed 객체를 저장합니다.
        self.feeds: List[Feed] = []

    def fit(self, feeds: List[Feed]):
        """
        추천 엔진을 주어진 Feed ORM 객체 리스트로 '학습'시킵니다.
        :param feeds: 추천 계산의 기반이 될 Feed 객체 리스트
        """
        logger.info(f"Fitting RecommendationEngine with {len(feeds)} feeds...")
        if not feeds:
            logger.warning("No feeds provided to fit the engine. Engine is not ready.")
            return

        self.feeds = feeds
        titles = [feed.title for feed in feeds]
        self.tfidf_matrix = self.vectorizer.fit_transform(titles)
        self.feed_map = {feed.id: i for i, feed in enumerate(feeds)}
        
        logger.info(f"Fitting complete. TF-IDF matrix shape: {self.tfidf_matrix.shape}")

    def get_recommendations(
        self,
        source_feed_id: int,
        target_content_type: str, # '정책자료' 또는 '보도자료'
        top_n: int = 5
    ) -> List[Tuple[int, float]]:
        """
        특정 피드와 유사한 다른 피드를 추천합니다.
        :param source_feed_id: 추천의 기준이 될 피드의 ID
        :param target_content_type: 추천 대상의 타입 ('정책자료' 또는 '보도자료')
        :param top_n: 추천할 피드의 개수
        :return: (추천된 피드 ID, 유사도 점수) 튜플의 리스트
        """
        if self.tfidf_matrix is None or not self.feeds:
            logger.error("Engine is not fitted yet. Call .fit() before getting recommendations.")
            return []
            
        if source_feed_id not in self.feed_map:
            logger.warning(f"Source feed with ID {source_feed_id} not found in the fitted data.")
            return []

        source_index = self.feed_map[source_feed_id]
        source_vector = self.tfidf_matrix[source_index]
        
        cosine_sims = cosine_similarity(source_vector, self.tfidf_matrix).flatten()
        
        # --- 👇 여기가 핵심 로직 변경 부분 ---
        
        # 1. '보도자료' 타입인지 여부를 확인하는 람다 함수 정의
        is_press_release = lambda feed: feed.category.name == PRESS_RELEASE_CATEGORY_NAME
        
        # 2. 추천 대상 피드들의 인덱스를 필터링합니다.
        target_indices = []
        for i, feed in enumerate(self.feeds):
            if feed.id == source_feed_id:
                continue # 자기 자신은 추천에서 제외

            # 현재 피드가 '보도자료'인지 판별
            current_feed_is_press = is_press_release(feed)

            # 조건에 맞는 경우에만 추천 대상에 추가
            if target_content_type == PRESS_RELEASE_CATEGORY_NAME and current_feed_is_press:
                target_indices.append(i)
            elif target_content_type != PRESS_RELEASE_CATEGORY_NAME and not current_feed_is_press:
                target_indices.append(i)

        if not target_indices:
            logger.info(f"No target feeds found with content_type '{target_content_type}'.")
            return []
            
        sim_scores = [(i, cosine_sims[i]) for i in target_indices]
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        top_scores = sim_scores[:top_n]
        
        recommendations = [(self.feeds[i].id, score) for i, score in top_scores]
        return recommendations