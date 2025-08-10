import { apiClient } from '@/lib/api/client';
import { 
    AdminSimpleOrganizationListResponse, 
    AdminOrganizationListResponse, 
    AdminOrganizationRequest, 
    AdminCategoryCreateRequest, 
    AdminCategoryUpdateRequest,
    AdminOrganizationCRUDResponse, 
    AdminCategoryCRUDResponse, 
    AdminDeleteResponse,
    AdminOrganizationDetailResponse, 
    AdminCategoryDetailResponse
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
export const createAdminOrganization = async (formData: FormData): Promise<AdminOrganizationCRUDResponse> => {
    const response = await apiClient.post<AdminOrganizationCRUDResponse>('/admin/organizations', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
};

/** 관리자: 기존 기관 정보를 수정 */
export const updateAdminOrganization = async (id: number, formData: FormData): Promise<AdminOrganizationCRUDResponse> => {
    // 💡 PATCH가 아닌 PUT을 사용하고, 파일 수정을 위해 _method 트릭을 사용할 수 있음
    // 하지만 API가 PATCH/JSON을 받는 것으로 수정되었으므로 그에 맞춤
    const payload: Partial<AdminOrganizationRequest> = {};
    formData.forEach((value, key) => (payload[key as keyof AdminOrganizationRequest] = value as any));
    
    // 파일은 별도로 처리해야 하므로, 우선은 텍스트 데이터만 업데이트하는 로직으로 가정
    // 실제로는 파일이 있다면 multipart/form-data로 보내야 함
    const response = await apiClient.patch<AdminOrganizationCRUDResponse>(`/admin/organizations/${id}`, payload);
    return response.data;
};

/** 관리자: 특정 기관을 삭제 */
export const deleteAdminOrganization = async (id: number): Promise<AdminDeleteResponse> => {
    const response = await apiClient.delete<AdminDeleteResponse>(`/admin/organizations/${id}`);
    return response.data;
};

/** 관리자: 새로운 카테고리를 생성 */
export const createAdminCategory = async (payload: AdminCategoryCreateRequest): Promise<AdminCategoryCRUDResponse> => {
    const response = await apiClient.post<AdminCategoryCRUDResponse>('/admin/organizations/categories', payload);
    return response.data;
};

/** 관리자: 기존 카테고리 정보를 수정 */
export const updateAdminCategory = async (id: number, payload: AdminCategoryUpdateRequest): Promise<AdminCategoryCRUDResponse> => {
    const response = await apiClient.patch<AdminCategoryCRUDResponse>(`/admin/organizations/categories/${id}`, payload);
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