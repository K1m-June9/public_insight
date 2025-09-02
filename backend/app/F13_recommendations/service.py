import logging
from typing import Union, List, Dict, Tuple

from app.F13_recommendations.engine import RecommendationEngine, PRESS_RELEASE_CATEGORY_NAME
from app.F13_recommendations.repository import RecommendationRepository
from app.F6_schemas.recommendation import (
    RecommendationResponse,
    RecommendationResultData,
    RecommendedFeedItem,
)
from app.F6_schemas.base import ErrorResponse, ErrorDetail, ErrorCode, Message
from app.F7_models.feeds import Feed

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    추천 관련 비즈니스 로직을 처리하는 서비스.
    리포지토리와 추천 엔진을 사용하여 최종 추천 결과를 생성함.
    """
    def __init__(self, repo: RecommendationRepository, engine: RecommendationEngine):
        self.repo = repo
        self.engine = engine

    async def get_recommendations_for_feed(self, feed_id: int) -> Union[RecommendationResponse, ErrorResponse]:
        """
        특정 피드에 대한 콘텐츠 기반 추천 목록을 반환함.
        엔진이 학습되지 않은 경우, 실시간으로 학습하여 추천을 제공함 (프로토타입 단계).
        """
        try:
            # 1. 추천 엔진이 학습되었는지 확인. 안 되었다면 실시간으로 학습시킴.
            # FIXME: 운영 환경에서는 이 로직이 서버 시작 시점에만 실행되어야 함. (dependencies.py에서 처리 예정)
            if not self.engine.feeds:
                logger.info("Recommendation engine is not fitted. Fitting in real-time...")
                all_feeds = await self.repo.get_all_feeds_for_fitting()
                if not all_feeds:
                    # 추천할 데이터가 없으므로 빈 결과를 반환함
                    return self._create_empty_recommendation_response()
                self.engine.fit(all_feeds)

            # 2. 기준 피드 정보 조회
            # engine.feeds는 최소 정보만 가지므로, category.name을 위해 순회하여 찾음.
            source_feed = next((feed for feed in self.engine.feeds if feed.id == feed_id), None)
            
            if not source_feed:
                return ErrorResponse(error=ErrorDetail(code=ErrorCode.NOT_FOUND, message=Message.FEED_NOT_FOUND))

            # 3. 기준 피드의 타입(정책자료/보도자료)을 판별함.
            is_source_press_release = source_feed.category.name == PRESS_RELEASE_CATEGORY_NAME
            
            # 4. 추천 타입에 따라 메인/서브 추천을 실행함.
            if is_source_press_release:
                main_reco_type = PRESS_RELEASE_CATEGORY_NAME
                sub_reco_type = "정책자료" # 보도자료가 아닌 모든 피드
            else:
                main_reco_type = "정책자료"
                sub_reco_type = PRESS_RELEASE_CATEGORY_NAME

            logger.info(f"[DEBUG] Main reco type: '{main_reco_type}', Sub reco type: '{sub_reco_type}'")
            main_reco_tuples = self.engine.get_recommendations(feed_id, main_reco_type)
            sub_reco_tuples = self.engine.get_recommendations(feed_id, sub_reco_type)

            
            # 5. 추천된 피드 ID 목록을 통합하여 DB에서 한 번에 조회함.
            all_reco_ids = list(set([feed_id for feed_id, score in main_reco_tuples] + [feed_id for feed_id, score in sub_reco_tuples]))
            recommended_feeds_map = {feed.id: feed for feed in await self.repo.get_feeds_by_ids(all_reco_ids)}

            # 6. 최종 응답 스키마에 맞게 데이터를 가공함.
            main_recommendations = self._format_recommendations(main_reco_tuples, recommended_feeds_map)
            sub_recommendations = self._format_recommendations(sub_reco_tuples, recommended_feeds_map)

            # 7. 최종 성공 응답을 반환함.
            return RecommendationResponse(
                data=RecommendationResultData(
                    main_recommendations=main_recommendations,
                    sub_recommendations=sub_recommendations,
                )
            )
        
        except Exception as e:
            logger.error(f"Error getting recommendations for feed_id {feed_id}: {e}", exc_info=True)
            return ErrorResponse(error=ErrorDetail(code=ErrorCode.INTERNAL_ERROR, message=Message.INTERNAL_ERROR))

    def _format_recommendations(self, reco_tuples: List[Tuple[int, float]], feeds_map: Dict[int, Feed]) -> List[RecommendedFeedItem]:
        """추천 결과 (ID, 점수)와 실제 Feed 객체를 조합하여 응답 스키마 형태로 변환함."""
        results = []
        for feed_id, score in reco_tuples:
            feed = feeds_map.get(feed_id)
            if feed:
                results.append(
                    RecommendedFeedItem(
                        id=feed.id,
                        title=feed.title,
                        summary=feed.summary,
                        organization_name=feed.organization.name,
                        category_name=feed.category.name,
                        published_date=feed.published_date,
                        similarity_score=round(score, 4) # 소수점 4자리까지 반올림
                    )
                )
        return results
    
    def _create_empty_recommendation_response(self) -> RecommendationResponse:
        """추천할 내용이 없을 때 반환할 비어있는 성공 응답을 생성함."""
        return RecommendationResponse(
            data=RecommendationResultData(
                main_recommendations=[],
                sub_recommendations=[],
            )
        )