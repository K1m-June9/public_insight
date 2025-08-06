import { apiClient } from '@/lib/api/client';
import { AdminSimpleOrganizationListResponse } from '@/lib/types/admin/organization';

/**
 * 관리자: 필터링에 사용할 간단한 기관 목록을 조회
 * @returns Promise<AdminSimpleOrganizationListResponse>
 */
export const getAdminSimpleOrganizationList = async (): Promise<AdminSimpleOrganizationListResponse> => {
    const response = await apiClient.get<AdminSimpleOrganizationListResponse>('/admin/organizations/list');
    return response.data;
};