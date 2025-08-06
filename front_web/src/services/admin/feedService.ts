import { apiClient } from '@/lib/api/client';
import {
    AdminFeedListResponse,
    AdminFeedListParams,
    AdminOrganizationCategoriesResponse,
    AdminFeedDetailResponse,
    AdminFeedUpdateResponse,
    AdminFeedUpdateRequest
} from '@/lib/types/admin/feed';

/**
 * 관리자: 필터링 및 페이지네이션을 적용하여 피드 목록을 조회
 * @param params - 검색, 필터, 페이지네이션 파라미터
 * @returns Promise<AdminFeedListResponse>
 */
export const getAdminFeedsList = async (params: AdminFeedListParams): Promise<AdminFeedListResponse> => {
    const response = await apiClient.get<AdminFeedListResponse>('/admin/feeds', { params });
    return response.data;
};

/**
 * 관리자: 특정 기관에 속한 카테고리 목록을 조회
 * (피드 생성/수정 및 필터링 UI에서 사용)
 * @param organizationId - 조회할 기관의 ID
 * @returns Promise<AdminOrganizationCategoriesResponse>
 */
export const getAdminOrganizationCategories = async (organizationId: number): Promise<AdminOrganizationCategoriesResponse> => {
    const response = await apiClient.get<AdminOrganizationCategoriesResponse>(`/admin/feeds/organizations/${organizationId}/categories`);
    return response.data;
};

/**
 * 관리자: ID로 특정 피드의 상세 정보를 조회
 * @param id - 조회할 피드의 ID
 * @returns Promise<AdminFeedDetailResponse>
 */
export const getAdminFeedDetail = async (id: number): Promise<AdminFeedDetailResponse> => {
    const response = await apiClient.get<AdminFeedDetailResponse>(`/admin/feeds/${id}`);
    return response.data;
};

/**
 * 관리자: 특정 피드의 정보를 수정
 * @param id - 수정할 피드의 ID
 * @param payload - 수정할 내용을 담은 객체
 * @returns Promise<AdminFeedUpdateResponse>
 */
export const updateAdminFeed = async (
    id: number,
    payload: AdminFeedUpdateRequest
): Promise<AdminFeedUpdateResponse> => {
    const response = await apiClient.put<AdminFeedUpdateResponse>(`/admin/feeds/${id}`, payload);
    return response.data;
};