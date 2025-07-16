import { useQuery } from '@tanstack/react-query';
import { getSearchResults } from '@/services/searchService';
import { SearchParams } from '@/lib/types/search';

// 검색 관련 쿼리 키를 관리하는 객체
export const searchQueryKeys = {
  all: ['search'] as const,
  lists: () => [...searchQueryKeys.all, 'list'] as const,
  list: (params: SearchParams) => [...searchQueryKeys.lists(), params] as const,
};

/**
 * 검색 결과를 조회하는 useQuery 훅
 * 검색어, 필터, 정렬, 페이지 등 모든 파라미터가 변경될 때마다 자동으로 데이터를 다시 가져옴
 * 
 * @param params - 검색에 필요한 모든 파라미터 객체
 * @param options - useQuery에 전달할 추가 옵션
 * @returns {data, isLoading, ...}
 */
export const useSearchQuery = (params: SearchParams, options?: { enabled?: boolean }) => {
  return useQuery({
    // queryKey에 모든 파라미터를 포함시켜, 파라미터가 바뀔 때마다 새로운 쿼리로 인식하게 함
    queryKey: searchQueryKeys.list(params),
    
    // queryFn은 항상 params를 인자로 받음
    queryFn: () => getSearchResults(params),

    // 검색어가 있을 때만 쿼리를 활성화합니다.
    enabled: options?.enabled ?? !!params.q,
    
    // 이전 데이터를 유지하여 페이지 이동 시 깜빡임을 방지
    placeholderData: (previousData) => previousData,
  });
};