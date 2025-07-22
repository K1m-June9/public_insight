import { apiClient } from '@/lib/api/client';
import { SearchResponse, SearchParams } from '@/lib/types/search';

/**
 * 검색 API를 호출하여 결과를 가져옴
 * @param params - 검색어, 필터, 정렬, 페이지네이션 등 모든 쿼리 파라미터
 * @returns Promise<SearchResponse>
 */
export const getSearchResults = async (params: SearchParams): Promise<SearchResponse> => {
  // 백엔드 라우터가 "/" 이므로, prefix인 "/search" 만으로 요청
  const response = await apiClient.get<SearchResponse>('/search', { params });
  return response.data;
};