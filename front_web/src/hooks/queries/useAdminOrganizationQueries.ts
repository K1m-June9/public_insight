import { useQuery } from '@tanstack/react-query';
import { getAdminSimpleOrganizationList } from '@/services/admin/organizationService';

/**
 * 관리자: 기관 관련 쿼리 키
 */
export const adminOrganizationQueryKeys = {
  all: ['admin', 'organizations'] as const,
  lists: () => [...adminOrganizationQueryKeys.all, 'list'] as const,
  simpleList: () => [...adminOrganizationQueryKeys.lists(), 'simple'] as const,
};

/**
 * 관리자: 필터링용 간단한 기관 목록을 조회하는 useQuery 훅
 */
export const useAdminSimpleOrganizationListQuery = () => {
  return useQuery({
    queryKey: adminOrganizationQueryKeys.simpleList(),
    queryFn: getAdminSimpleOrganizationList,
    staleTime: 1000 * 60 * 60, // 1시간. 기관 목록은 거의 바뀌지 않으므로 캐시를 길게 유지.
  });
};