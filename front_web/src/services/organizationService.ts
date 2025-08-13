import { apiClient } from '@/lib/api/client';
import {
    OrganizationListResponse,
    OrganizationCategoryResponse,
    WordCloudResponse,
    OrganizationIconResponse, // 추후 삭제 예정이지만 지금은 쓸거같은 타입
    OrganizationSummaryResponse
} from '@/lib/types/organization';

/**
* 메인 페이지 원형 그래프에 사용될 기관 목록과 비율을 조회
* @returns Promise<OrganizationListResponse>
*/
export const getOrganizationsForChart = async (): Promise<OrganizationListResponse> => {
    const response = await apiClient.get<OrganizationListResponse>('/organizations/');
    return response.data;
};

/**
* 특정 기관의 카테고리 목록과 비율을 조회
* @param name - 기관명
* @returns Promise<OrganizationCategoryResponse>
*/
export const getOrganizationCategoriesForChart = async (name: string): Promise<OrganizationCategoryResponse> => {
    const response = await apiClient.get<OrganizationCategoryResponse>(`/organizations/${name}/categories`);
    return response.data;
};

/**
* 특정 기관의 아이콘(Base64)을 조회
* 아마도 나중에 삭제 예정인 API 호출
* API 호출 방식 -> Static URL 예정
* 아 이런거 알았으면 진작에 썼을텐데 왜 아무도 나한테 안알려준거임
* 나중에 수정하기 싫다~~~~~~~~~~~~~~~~~~~~~~~~~~~~~₩
* @param name - 기관명
* @returns Promise<OrganizationIconResponse>
*/
export const getOrganizationIcon = async (name: string): Promise<OrganizationIconResponse> => {
    const response = await apiClient.get<OrganizationIconResponse>(`/organizations/${name}/icon`);
    return response.data;
};

/**
* 특정 기관의 워드클라우드 데이터를 조회
* @param name - 기관명
* @returns Promise<WordCloudResponse>
*/
export const getOrganizationWordCloud = async (name: string): Promise<WordCloudResponse> => {
    const response = await apiClient.get<WordCloudResponse>(`/organizations/${name}/wordcloud`);
    return response.data;
};

/**
 * 특정 기관의 요약 정보(이름, 설명, 통계)를 조회
 * @param name - 기관명
 * @returns Promise<OrganizationSummaryResponse>
 */
export const getOrganizationSummary = async (name: string): Promise<OrganizationSummaryResponse> => {
    const response = await apiClient.get<OrganizationSummaryResponse>(`/organizations/${name}/summary`);
    return response.data;
};