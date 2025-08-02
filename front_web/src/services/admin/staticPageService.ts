import { apiClient } from '@/lib/api/client';
import { AdminStaticPageListResponse } from '@/lib/types/admin/staticPage';

/**
 * 관리자: 모든 정적 페이지 목록을 조회
 * @returns Promise<AdminStaticPageListResponse>
 */
export const getAdminStaticPages = async (): Promise<AdminStaticPageListResponse> => {
    const response = await apiClient.get<AdminStaticPageListResponse>('/admin/static-pages');
    return response.data;
};