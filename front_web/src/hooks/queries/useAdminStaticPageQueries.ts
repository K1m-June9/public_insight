import { useQuery } from '@tanstack/react-query';
import { getAdminStaticPages } from '@/services/admin/staticPageService';

/**
 * 관리자: 정적 페이지 목록 조회를 위한 쿼리 키
 */
export const adminStaticPageQueryKeys = {
  all: ['admin', 'static-pages'] as const,
  lists: () => [...adminStaticPageQueryKeys.all, 'list'] as const,
};

/**
 * 관리자: 모든 정적 페이지 목록을 조회하는 useQuery 훅
 * 
 * @param options - useQuery에 전달할 추가 옵션 (staleTime 등)
 * @returns {data, isLoading, isError, ...}
 */
export const useAdminStaticPagesQuery = (options?: { staleTime?: number }) => {
  return useQuery({
    queryKey: adminStaticPageQueryKeys.lists(),
    queryFn: getAdminStaticPages,
    staleTime: options?.staleTime ?? 1000 * 60, // 기본 1분
    // 관리자 페이지는 보통 관리자 본인만 사용하므로,
    // 창에 다시 포커스할 때마다 데이터를 새로고침할 필요가 없을 수 있음
    // refetchOnWindowFocus: false, // 필요 시 이 옵션을 추가할 수 있음
  });
};