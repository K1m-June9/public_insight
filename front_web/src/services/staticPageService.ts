import { apiClient } from '@/lib/api/client';
import { StaticPageResponse } from '@/lib/types/static_page';

/**
* slug에 해당하는 정적 페이지의 내용을 조회
* @param slug - 페이지 식별자 **지원 slug**: about, terms, privacy, youth-protection
* @returns Promise<StaticPageResponse>
*/
export const getStaticPage = async (slug: string): Promise<StaticPageResponse> => {
    const response = await apiClient.get<StaticPageResponse>(`/static-pages/${slug}`);
    return response.data;
};