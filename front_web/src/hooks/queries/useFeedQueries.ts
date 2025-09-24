import { useQuery } from '@tanstack/react-query';
import {
    getFeeds,
    getOrganizationFeeds,
    getLatestFeeds,
    getOrganizationLatestFeeds,
    getTop5Feeds,
    getPressReleases,
    getFeedDetail,
    getFeedRecommendations,
} from '@/services/feedService';

interface PaginationParams {
    page?: number;
    limit?: number;
}

interface CategoryFilterParams extends PaginationParams {
    category_id?: number;
}

// 피드 관련 쿼리 키를 관리하는 객체
export const feedQueryKeys = {
    all: ['feeds'] as const,
    lists: () => [...feedQueryKeys.all, 'list'] as const,
    list: (params: any) => [...feedQueryKeys.lists(), params] as const,
    details: () => [...feedQueryKeys.all, 'detail'] as const,
    detail: (id: number) => [...feedQueryKeys.details(), id] as const,
    recommendations: (id: number) => [...feedQueryKeys.detail(id), 'recommendations'] as const,
};

/**
 * 메인 페이지 피드 목록을 조회하는 useQuery 훅
 */
export const useFeedsQuery = (params: PaginationParams) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ ...params, scope: 'main' }),
        queryFn: () => getFeeds(params),
        placeholderData: (previousData) => previousData,
    });
};

/**
 * 특정 기관의 피드 목록을 조회하는 useQuery 훅
 */
export const useOrganizationFeedsQuery = (name: string, params: CategoryFilterParams) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ ...params, organization: name }),
        queryFn: () => getOrganizationFeeds(name, params),
        enabled: !!name,
        placeholderData: (previousData) => previousData,
    });
};

/**
 * 메인 페이지의 최신 피드 슬라이드를 조회하는 useQuery 훅
 */
export const useLatestFeedsQuery = (limit: number) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ scope: 'latest', limit }),
        queryFn: () => getLatestFeeds(limit),
        staleTime: 1000 * 60 * 5, // 5분
    });
};

/**
 * 특정 기관의 최신 피드 슬라이드를 조회하는 useQuery 훅
 */
export const useOrganizationLatestFeedsQuery = (name: string, limit: number) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ scope: 'latest', organization: name, limit }),
        queryFn: () => getOrganizationLatestFeeds(name, limit),
        enabled: !!name,
        staleTime: 1000 * 60 * 5, // 5분
    });
};

/**
 * 메인 페이지의 TOP 5 피드 목록을 조회하는 useQuery 훅
 */
export const useTop5FeedsQuery = (limit: number) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ scope: 'top5', limit }),
        queryFn: () => getTop5Feeds(limit),
        staleTime: 1000 * 60 * 10, // 10분
    });
};

/**
 * 특정 기관의 보도자료 목록을 조회하는 useQuery 훅
 */
export const usePressReleasesQuery = (name: string, params: PaginationParams) => {
    return useQuery({
        queryKey: feedQueryKeys.list({ ...params, scope: 'press', organization: name }),
        queryFn: () => getPressReleases(name, params),
        enabled: !!name,
        placeholderData: (previousData) => previousData,
    });
};

/**
 * 특정 피드의 상세 정보를 조회하는 useQuery 훅
 */
export const useFeedDetailQuery = (id: number, options?: { enabled?: boolean }) => {
    return useQuery({
        queryKey: feedQueryKeys.detail(id),
        queryFn: () => getFeedDetail(id),
        enabled: options?.enabled ?? !!id,
    });
};

/**
 * 특정 피드에 대한 추천 목록을 조회하는 useQuery 훅
 * @param feedId - 추천의 기준이 될 피드 ID
 */
export const useFeedRecommendationsQuery = (feedId: number | null) => {
    return useQuery({
        queryKey: feedQueryKeys.recommendations(feedId!), // 👈 [수정] id가 null일 수 있으므로 non-null assertion(!) 추가
        queryFn: () => getFeedRecommendations(feedId!),
        enabled: !!feedId, // feedId가 있을 때만 훅을 활성화
        staleTime: 1000 * 60 * 5, // 5분. 추천 목록은 자주 바뀌지 않음
    });
};