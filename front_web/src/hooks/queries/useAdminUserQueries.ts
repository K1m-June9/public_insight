import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { getAdminUsers, getAdminUserDetail, getAdminUserActivities } from '@/services/admin/userService';
import { AdminUserListRequestParams } from '@/lib/types/admin/user';

/**
 * 관리자: 사용자 관련 쿼리 키
 */
export const adminUserQueryKeys = {
  all: ['admin', 'users'] as const,
  lists: () => [...adminUserQueryKeys.all, 'list'] as const,
  list: (filters: AdminUserListRequestParams) => [...adminUserQueryKeys.lists(), filters] as const,
  details: () => [...adminUserQueryKeys.all, 'detail'] as const,
  detail: (id: string | null) => [...adminUserQueryKeys.details(), id] as const,
  activities: (id: string | null) => [...adminUserQueryKeys.detail(id), 'activities'] as const,
};

/**
 * 관리자: 사용자 목록을 조회하는 useQuery 훅
 * @param filters - 필터링 및 페이지네이션 파라미터
 */
export const useAdminUsersQuery = (filters: AdminUserListRequestParams) => {
  return useQuery({
    queryKey: adminUserQueryKeys.list(filters),
    queryFn: () => getAdminUsers(filters),
    staleTime: 1000 * 60, // 1분
  });
};

/**
 * 관리자: 특정 사용자의 상세 정보를 조회하는 useQuery 훅
 * @param id - 조회할 사용자의 user_id (문자열)
 */
export const useAdminUserDetailQuery = (id: string | null) => {
  return useQuery({
    queryKey: adminUserQueryKeys.detail(id),
    queryFn: () => getAdminUserDetail(id!),
    enabled: !!id,
  });
};

/**
 * 관리자: 특정 사용자의 활동 로그를 '더보기' 방식으로 조회하는 useInfiniteQuery 훅
 * @param id - 조회할 사용자의 user_id (문자열)
 */
export const useAdminUserActivitiesInfiniteQuery = (id: string | null) => {
  return useInfiniteQuery({
    queryKey: adminUserQueryKeys.activities(id),
    queryFn: ({ pageParam = 1 }) => getAdminUserActivities(id!, { page: pageParam, limit: 50 }),
    getNextPageParam: (lastPage) => {
      const pagination = lastPage.data.pagination;
      return pagination.has_next ? pagination.current_page + 1 : undefined;
    },
    initialPageParam: 1,
    enabled: !!id,
  });
};