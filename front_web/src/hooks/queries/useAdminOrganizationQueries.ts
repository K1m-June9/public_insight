import { useQuery } from '@tanstack/react-query';
import { getAdminSimpleOrganizationList, getAdminOrganizationsList, getAdminOrganizationDetail, getAdminCategoryDetail } from '@/services/admin/organizationService';

/**
 * 관리자: 기관 관련 쿼리 키
 */
export const adminOrganizationQueryKeys = {
  all: ['admin', 'organizations'] as const,
  lists: () => [...adminOrganizationQueryKeys.all, 'list'] as const,
  simpleList: () => [...adminOrganizationQueryKeys.lists(), 'simple'] as const,
  fullList: () => [...adminOrganizationQueryKeys.lists(), 'full'] as const,
  details: () => [...adminOrganizationQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...adminOrganizationQueryKeys.details(), id] as const,
  categoryDetails: () => [...adminOrganizationQueryKeys.all, 'category-detail'] as const,
  categoryDetail: (id: number) => [...adminOrganizationQueryKeys.categoryDetails(), id] as const,
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

/**
 * 관리자: 모든 기관과 카테고리 정보를 포함한 전체 목록을 조회하는 useQuery 훅
 */
export const useAdminOrganizationsListQuery = () => {
  return useQuery({
    queryKey: adminOrganizationQueryKeys.fullList(),
    queryFn: getAdminOrganizationsList,
    staleTime: 1000 * 60 * 5, // 5분
  });
};

/**
 * 관리자: 특정 기관의 상세 정보를 조회하는 useQuery 훅
 */
export const useAdminOrganizationDetailQuery = (id: number | null) => {
    return useQuery({
        queryKey: adminOrganizationQueryKeys.detail(id!),
        queryFn: () => getAdminOrganizationDetail(id!),
        enabled: !!id,
    });
};

/**
 * 관리자: 특정 카테고리의 상세 정보를 조회하는 useQuery 훅
 */
export const useAdminCategoryDetailQuery = (id: number | null) => {
    return useQuery({
        queryKey: adminOrganizationQueryKeys.categoryDetail(id!),
        queryFn: () => getAdminCategoryDetail(id!),
        enabled: !!id,
    });
};