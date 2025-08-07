import { apiClient } from '@/lib/api/client';
import { AdminSimpleOrganizationListResponse, AdminOrganizationListResponse } from '@/lib/types/admin/organization';

/**
 * 관리자: 필터링에 사용할 간단한 기관 목록을 조회
 * @returns Promise<AdminSimpleOrganizationListResponse>
 */
export const getAdminSimpleOrganizationList = async (): Promise<AdminSimpleOrganizationListResponse> => {
    const response = await apiClient.get<AdminSimpleOrganizationListResponse>('/admin/organizations/list');
    return response.data;
};

/**
 * 관리자: 모든 기관과 각 기관에 속한 카테고리 목록을 조회
 * @returns Promise<AdminOrganizationListResponse>
 */
export const getAdminOrganizationsList = async (): Promise<AdminOrganizationListResponse> => {
    const response = await apiClient.get<AdminOrganizationListResponse>('/admin/organizations');
    return response.data;
};