import logging
from typing import List, Dict, Tuple
import threading # 👈 [추가] 스레드 동기화를 위한 Lock

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.F7_models.feeds import Feed
from app.F7_models.categories import Category

logger = logging.getLogger(__name__)
PRESS_RELEASE_CATEGORY_NAME = "보도자료"

class RecommendationEngine:
    """
    TF-IDF와 코사인 유사도를 기반으로 콘텐츠 기반 추천을 수행하는 엔진.
    이 객체는 싱글톤으로 관리되며, 상태 변경은 스레드에 안전해야 함.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        self.tfidf_matrix = None
        self.feed_map: Dict[int, int] = {}
        self.feeds: List[Feed] = []
        # 👈 [추가] 데이터 업데이트 시 동시성 문제를 방지하기 위한 Lock 객체
        self._lock = threading.Lock()

    def fit(self, feeds: List[Feed]):
        """
        추천 엔진을 주어진 피드 데이터로 '학습'시킴.
        이 메서드는 객체 초기화 시에만 호출되어야 함.
        """
        logger.info(f"Fitting RecommendationEngine with {len(feeds)} feeds...")
        if not feeds:
            logger.warning("No feeds provided to fit the engine.")
            return
        
        # 💥 스레드 안전성을 위해 with 문으로 Lock을 획득함
        with self._lock:
            self.feeds = feeds
            titles = [feed.title for feed in feeds]
            self.tfidf_matrix = self.vectorizer.fit_transform(titles)
            self.feed_map = {feed.id: i for i, feed in enumerate(feeds)}
            logger.info(f"Fitting complete. TF-IDF matrix shape: {self.tfidf_matrix.shape}")

    def refit(self, feeds: List[Feed]):
        """
        [신규] 새로운 피드 데이터로 엔진을 '재학습'시킴.
        주기적 스케줄러에 의해 호출될 메서드임.
        """
        logger.info(f"Refitting RecommendationEngine with {len(feeds)} new feeds...")
        if not feeds:
            logger.warning("No feeds provided for refitting. Engine state remains unchanged.")
            return

        # 새로운 데이터로 TF-IDF 모델과 행렬을 다시 생성함
        new_vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        titles = [feed.title for feed in feeds]
        new_tfidf_matrix = new_vectorizer.fit_transform(titles)
        new_feed_map = {feed.id: i for i, feed in enumerate(feeds)}
        
        # 💥 Lock을 획득하고, 학습된 모든 데이터를 원자적으로(atomically) 교체함
        with self._lock:
            self.vectorizer = new_vectorizer
            self.tfidf_matrix = new_tfidf_matrix
            self.feeds = feeds
            self.feed_map = new_feed_map
        
        logger.info(f"Refitting complete. New TF-IDF matrix shape: {self.tfidf_matrix.shape}")

    def get_recommendations(self, source_feed_id: int, target_content_type: str, top_n: int = 5) -> List[Tuple[int, float]]:
        """
        특정 피드와 유사한 다른 피드를 추천함. (이 메서드는 변경 없음)
        """
        # 💥 읽기 작업 중에도 데이터가 변경될 수 있으므로, Lock을 사용하여 일관성을 보장함
        with self._lock:
            if self.tfidf_matrix is None or not self.feeds:
                logger.error("Engine is not fitted yet.")
                return []
            
            if source_feed_id not in self.feed_map:
                logger.warning(f"Source feed with ID {source_feed_id} not found.")
                return []

            source_index = self.feed_map[source_feed_id]
            source_vector = self.tfidf_matrix[source_index]
            
            cosine_sims = cosine_similarity(source_vector, self.tfidf_matrix).flatten()
            
            is_press_release = lambda feed: feed.category.name == PRESS_RELEASE_CATEGORY_NAME
            
            target_indices = []
            for i, feed in enumerate(self.feeds):
                if feed.id == source_feed_id: continue

                current_feed_is_press = is_press_release(feed)

                if target_content_type == PRESS_RELEASE_CATEGORY_NAME and current_feed_is_press:
                    target_indices.append(i)
                elif target_content_type != PRESS_RELEASE_CATEGORY_NAME and not current_feed_is_press:
                    target_indices.append(i)

            if not target_indices: return []
                
            sim_scores = [(i, cosine_sims[i]) for i in target_indices]
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            top_scores = sim_scores[:top_n]
            
            recommendations = [(self.feeds[i].id, score) for i, score in top_scores]
            return recommendations