import { useQuery } from '@tanstack/react-query';
import { getMyProfile, getMyRatings, getMyBookmarks, getUserRecommendations } from '@/services/userService';

interface PaginationParams {
    page?: number;
    limit?: number;
}

// 사용자 관련 쿼리 키를 관리하는 객체
export const userQueryKeys = {
  all: ['users'] as const,
  me: () => [...userQueryKeys.all, 'me'] as const,
  lists: () => [...userQueryKeys.all, 'lists'] as const,
  ratings: (params: PaginationParams) => [...userQueryKeys.lists(), 'ratings', params] as const,
  bookmarks: (params: PaginationParams) => [...userQueryKeys.lists(), 'bookmarks', params] as const,
  recommendations: () => [...userQueryKeys.me(), 'recommendations'] as const,
};

/**
 * 현재 로그인된 사용자의 프로필 정보를 조회하는 useQuery 훅
 * AuthContext와 연동하여, 로그인 상태일 때만 실행
 * 
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useMyProfileQuery = (options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: userQueryKeys.me(),
    queryFn: getMyProfile,
    enabled: options?.enabled, // AuthContext에서 로그인 여부를 받아와 enabled에 전달
    staleTime: 1000 * 60 * 5, // 5분 동안 프로필 정보는 신선한 상태로 유지
  });
};

/**
 * 현재 로그인된 사용자의 별점 목록을 조회하는 useQuery 훅
 * 
 * @param params - 페이지네이션 파라미터 (page, limit)
 * @returns {data, isLoading, ...}
 */
export const useMyRatingsQuery = (params: PaginationParams) => {
  return useQuery({
    queryKey: userQueryKeys.ratings(params),
    queryFn: () => getMyRatings(params),
    placeholderData: (previousData) => previousData, // 새 페이지 로드 시 이전 데이터 유지
  });
};

/**
 * 현재 로그인된 사용자의 북마크 목록을 조회하는 useQuery 훅
 * 
 * @param params - 페이지네이션 파라미터 (page, limit)
 * @returns {data, isLoading, ...}
 */
export const useMyBookmarksQuery = (params: PaginationParams) => {
  return useQuery({
    queryKey: userQueryKeys.bookmarks(params),
    queryFn: () => getMyBookmarks(params),
    placeholderData: (previousData) => previousData,
  });
};

/**
 * 현재 로그인된 사용자의 맞춤 추천 목록을 조회하는 useQuery 훅
 * @returns {data, isLoading, ...}
 */
export const useUserRecommendationsQuery = () => {
  return useQuery({
    // << [추가] 새로 정의한 쿼리 키를 사용
    queryKey: userQueryKeys.recommendations(),
    // << [추가] 새로 정의한 서비스 함수를 호출
    queryFn: getUserRecommendations,
    // 추천 데이터는 자주 바뀌지 않으므로, 10분 정도 staleTime을 설정하여 불필요한 API 호출을 줄임
    staleTime: 1000 * 60 * 10,
  });
};