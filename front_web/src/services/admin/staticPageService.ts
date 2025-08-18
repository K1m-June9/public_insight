import { apiClient } from '@/lib/api/client';
import { 
    AdminStaticPageListResponse,
    AdminStaticPageDetailResponse,
    AdminStaticPageUpdateRequest,
    AdminStaticPageUpdateResponse 
} from '@/lib/types/admin/staticPage';

/**
 * 관리자: 모든 정적 페이지 목록을 조회
 * @returns Promise<AdminStaticPageListResponse>
 */
export const getAdminStaticPages = async (): Promise<AdminStaticPageListResponse> => {
    const response = await apiClient.get<AdminStaticPageListResponse>('/admin/static-pages');
    return response.data;
};

/**
 * 관리자: slug로 특정 정적 페이지의 상세 정보를 조회
 * @param slug - 조회할 페이지의 slug
 * @returns Promise<AdminStaticPageDetailResponse>
 */
export const getAdminStaticPageDetail = async (slug: string): Promise<AdminStaticPageDetailResponse> => {
    const response = await apiClient.get<AdminStaticPageDetailResponse>(`/admin/static-pages/${slug}`);
    return response.data;
};

/**
 * 관리자: 특정 정적 페이지의 내용을 수정
 * @param slug - 수정할 페이지의 slug
 * @param payload - 새로운 content를 담은 객체
 * @returns Promise<AdminStaticPageUpdateResponse>
 */
export const updateAdminStaticPage = async (
    slug: string, 
    payload: AdminStaticPageUpdateRequest
): Promise<AdminStaticPageUpdateResponse> => {
    const response = await apiClient.put<AdminStaticPageUpdateResponse>(`/admin/static-pages/${slug}`, payload);
    return response.data;
};