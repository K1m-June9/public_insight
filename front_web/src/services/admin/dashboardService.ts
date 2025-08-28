import { apiClient } from '@/lib/api/client';
import { AdminDashboardResponse } from '@/lib/types/admin/dashboard';

/**
 * 관리자: 대시보드에 필요한 모든 통계 데이터를 조회
 */
export const getAdminDashboardStats = async (): Promise<AdminDashboardResponse> => {
  const response = await apiClient.get<AdminDashboardResponse>('/admin/dashboard');
  return response.data;
};