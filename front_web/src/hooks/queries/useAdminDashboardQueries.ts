import { useQuery } from '@tanstack/react-query';
import { getAdminDashboardStats } from '@/services/admin/dashboardService';

/**
 * 관리자: 대시보드 관련 쿼리 키
 */
export const adminDashboardQueryKeys = {
  all: ['admin', 'dashboard'] as const,
  stats: () => [...adminDashboardQueryKeys.all, 'stats'] as const,
};

/**
 * 관리자: 대시보드 통계 데이터를 조회하는 useQuery 훅
 */
export const useAdminDashboardQuery = () => {
  return useQuery({
    queryKey: adminDashboardQueryKeys.stats(),
    queryFn: getAdminDashboardStats,
    // 대시보드 데이터는 자주 변경될 수 있으므로, staleTime을 비교적 짧게 설정
    staleTime: 1000 * 60, // 1분
    // 대시보드는 최신 정보를 보는 것이 중요하므로, 창 포커스 시 새로고침을 활성화
    refetchOnWindowFocus: true,
  });
};