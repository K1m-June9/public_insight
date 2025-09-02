import { apiClient } from '@/lib/api/client';
import {
    MainFeedListResponse,
    OrganizationFeedListResponse,
    LatestFeedResponse,
    OrganizationLatestFeedResponse,
    Top5FeedResponse,
    PressReleaseResponse,
    FeedDetailResponse,
    RatingResponse,
    BookmarkResponse,
    RecommendationResponse
} from '@/lib/types/feed';

interface PaginationParams {
    page?: number;
    limit?: number;
}

interface CategoryFilterParams extends PaginationParams {
    category_id?: number;
}

// =================================
// 피드 목록 조회
// =================================

/**
* 메인 페이지의 피드 목록을 조회
* @param params - 페이지네이션 파라미터
* @returns Promise<MainFeedListResponse>
*/
export const getFeeds = async (params: PaginationParams): Promise<MainFeedListResponse> => {
    // 백엔드 라우터가 "/" 이므로, prefix인 "/feeds" 만으로 요청
    const response = await apiClient.get<MainFeedListResponse>('/feeds/', { params });
    return response.data;
};

/**
* 특정 기관의 피드 목록을 조회
* @param name - 기관명
* @param params - 페이지네이션 및 카테고리 필터 파라미터
* @returns Promise<OrganizationFeedListResponse>
*/
export const getOrganizationFeeds = async (name: string, params: CategoryFilterParams): Promise<OrganizationFeedListResponse> => {
    const response = await apiClient.get<OrganizationFeedListResponse>(`/feeds/${name}`, { params });
    return response.data;
};

/**
* 메인 페이지의 최신 피드 슬라이드 목록을 조회
* @param limit - 가져올 피드 수
* @returns Promise<LatestFeedResponse>
*/
export const getLatestFeeds = async (limit: number): Promise<LatestFeedResponse> => {
    const response = await apiClient.get<LatestFeedResponse>('/feeds/latest', { params: { limit } });
    return response.data;
};

/**
* 특정 기관의 최신 피드 슬라이드 목록을 조회
* @param name - 기관명
* @param limit - 가져올 피드 수
* @returns Promise<OrganizationLatestFeedResponse>
*/
export const getOrganizationLatestFeeds = async (name: string, limit: number): Promise<OrganizationLatestFeedResponse> => {
    const response = await apiClient.get<OrganizationLatestFeedResponse>(`/feeds/${name}/latest`, { params: { limit } });
    return response.data;
};

/**
* 메인 페이지의 TOP 5 피드 목록을 조회 (별점순, 조회수순, 북마크순)
* @param limit - 각 카테고리별로 가져올 피드 수
* @returns Promise<Top5FeedResponse>
*/
export const getTop5Feeds = async (limit: number): Promise<Top5FeedResponse> => {
    const response = await apiClient.get<Top5FeedResponse>('/feeds/top5', { params: { limit } });
    return response.data;
};

/**
* 특정 기관의 보도자료 목록을 조회
* 나는 참 이게 애매애매애매
* @param name - 기관명
* @param params - 페이지네이션 파라미터
* @returns Promise<PressReleaseResponse>
*/
export const getPressReleases = async (name: string, params: PaginationParams): Promise<PressReleaseResponse> => {
    const response = await apiClient.get<PressReleaseResponse>(`/feeds/${name}/press`, { params });
    return response.data;
};

// =================================
// 피드 상세 및 상호작용
// =================================

/**
* 특정 피드의 상세 정보를 조회
* @param id - 피드의 고유 ID
* @returns Promise<FeedDetailResponse>
*/
export const getFeedDetail = async (id: number): Promise<FeedDetailResponse> => {
    // const response = await apiClient.get<FeedDetailResponse>(`/feeds/${id}`);
    const response = await apiClient.get<FeedDetailResponse>(`/feeds/detail/${id}`);
    return response.data;
};

/**
* 특정 피드에 별점을 메김 (생성)
* @param id - 피드의 고유 ID
* @param score - 1~5점 사이의 별점
* @returns Promise<RatingResponse>
*/
export const postRating = async (id: number, score: number): Promise<RatingResponse> => {
    // const response = await apiClient.post<RatingResponse>(`/feeds/${id}/ratings`, { score });
    const response = await apiClient.post<RatingResponse>(`/feeds/detail/${id}/ratings`, { score });
    return response.data;
};

/**
* 특정 피드를 북마크하거나 북마크를 취소 (토글방식이니까)
* @param id - 피드의 고유 ID
* @returns Promise<BookmarkResponse>
*/
export const toggleBookmark = async (id: number): Promise<BookmarkResponse> => {
    // 요청 본문이 비어있으므로 빈 객체를 보냄(차라차라참참참 신기해)
    // const response = await apiClient.post<BookmarkResponse>(`/feeds/${id}/bookmark`, {});
    const response = await apiClient.post<BookmarkResponse>(`/feeds/detail/${id}/bookmark`, {});
    return response.data;
};

/**
 * 특정 피드와 관련된 추천 피드 목록을 조회
 * @param id - 기준이 되는 피드의 ID
 * @returns Promise<RecommendationResponse>
 */
export const getFeedRecommendations = async (id: number): Promise<RecommendationResponse> => {
  const response = await apiClient.get<RecommendationResponse>(`/feeds/detail/${id}/recommendations`);
  return response.data;
};