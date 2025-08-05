import { useQuery } from '@tanstack/react-query';
import { getAdminFeedsList, getAdminOrganizationCategories } from '@/services/admin/feedService';
import { AdminFeedListParams } from '@/lib/types/admin/feed';

/**
 * 관리자: 피드 관련 쿼리 키
 */
export const adminFeedQueryKeys = {
  all: ['admin', 'feeds'] as const,
  lists: () => [...adminFeedQueryKeys.all, 'list'] as const,
  list: (params: AdminFeedListParams) => [...adminFeedQueryKeys.lists(), params] as const,
  categories: () => [...adminFeedQueryKeys.all, 'categories'] as const,
  categoryList: (orgId: number) => [...adminFeedQueryKeys.categories(), orgId] as const,
};

/**
 * 관리자: 피드 목록을 조회하는 useQuery 훅
 * 
 * @param params - 검색, 필터, 페이지네이션 파라미터
 * @returns {data, isLoading, ...}
 */
export const useAdminFeedsListQuery = (params: AdminFeedListParams) => {
  return useQuery({
    queryKey: adminFeedQueryKeys.list(params),
    queryFn: () => getAdminFeedsList(params),
    placeholderData: (previousData) => previousData, // 페이지 이동 시 UI 깜빡임 방지
  });
};

/**
 * 관리자: 특정 기관의 카테고리 목록을 조회하는 useQuery 훅
 * 
 * @param organizationId - 조회할 기관의 ID
 * @returns {data, isLoading, ...}
 */
export const useAdminOrganizationCategoriesQuery = (organizationId: number | null) => {
  return useQuery({
    queryKey: adminFeedQueryKeys.categoryList(organizationId!), // non-null assertion '!' 사용
    queryFn: () => getAdminOrganizationCategories(organizationId!),
    // 💡 organizationId가 null이 아닐 때만 쿼리를 실행합니다.
    enabled: organizationId !== null && organizationId > 0,
    staleTime: 1000 * 60 * 5, // 카테고리 목록은 자주 바뀌지 않으므로 5분간 캐시 유지
  });
};