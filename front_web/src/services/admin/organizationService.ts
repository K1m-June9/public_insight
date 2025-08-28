import { apiClient } from '@/lib/api/client';
import { 
    AdminSimpleOrganizationListResponse, 
    AdminOrganizationListResponse, 
    AdminOrganizationRequest, 
    AdminCategoryCreateRequest, 
    AdminCategoryUpdateRequest,
    AdminOrganizationCreateResponse,
    AdminOrganizationUpdateResponse,
    AdminDeleteResponse,
    AdminOrganizationDetailResponse, 
    AdminCategoryDetailResponse,
    AdminCategoryCreateResponse,
    AdminCategoryUpdateResponse,
} from '@/lib/types/admin/organization';

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

/** 관리자: 새로운 기관을 생성 */
// 반환 타입을 AdminOrganizationCreateResponse로 수정
export const createAdminOrganization = async (payload: AdminOrganizationRequest): Promise<AdminOrganizationCreateResponse> => {
    const response = await apiClient.post<AdminOrganizationCreateResponse>('/admin/organizations', payload);
    return response.data;
};

/** 관리자: 기존 기관 정보를 수정 */
// 반환 타입을 AdminOrganizationUpdateResponse로 수정
export const updateAdminOrganization = async (id: number, payload: AdminOrganizationRequest): Promise<AdminOrganizationUpdateResponse> => {
    const response = await apiClient.patch<AdminOrganizationUpdateResponse>(`/admin/organizations/${id}`, payload);
    return response.data;
};

/** 관리자: 특정 기관을 삭제 */
export const deleteAdminOrganization = async (id: number): Promise<AdminDeleteResponse> => {
    const response = await apiClient.delete<AdminDeleteResponse>(`/admin/organizations/${id}`);
    return response.data;
};

/** 관리자: 새로운 카테고리를 생성 */
export const createAdminCategory = async (payload: AdminCategoryCreateRequest): Promise<AdminCategoryCreateResponse> => {
    const response = await apiClient.post<AdminCategoryCreateResponse>('/admin/organizations/categories', payload);
    return response.data;
};

/** 관리자: 기존 카테고리 정보를 수정 */
export const updateAdminCategory = async (id: number, payload: AdminCategoryUpdateRequest): Promise<AdminCategoryUpdateResponse> => {
    const response = await apiClient.patch<AdminCategoryUpdateResponse>(`/admin/organizations/categories/${id}`, payload);
    return response.data;
};

/** 관리자: 특정 카테고리를 삭제 */
export const deleteAdminCategory = async (id: number): Promise<AdminDeleteResponse> => {
    const response = await apiClient.delete<AdminDeleteResponse>(`/admin/organizations/categories/${id}`);
    return response.data;
};

/** 관리자: 특정 기관의 상세 정보를 조회 */
export const getAdminOrganizationDetail = async (id: number): Promise<AdminOrganizationDetailResponse> => {
    const response = await apiClient.get<AdminOrganizationDetailResponse>(`/admin/organizations/${id}`);
    return response.data;
};

/** 관리자: 특정 카테고리의 상세 정보를 조회 */
export const getAdminCategoryDetail = async (id: number): Promise<AdminCategoryDetailResponse> => {
    const response = await apiClient.get<AdminCategoryDetailResponse>(`/admin/organizations/categories/${id}`);
    return response.data;
};