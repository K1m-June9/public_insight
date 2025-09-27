import { useQuery } from '@tanstack/react-query';
import { getWordCloudData, getExploreData, getExpandData } from '@/services/graphService';

// graph 관련 쿼리 키를 관리하는 객체
export const graphQueryKeys = {
  all: ['graph'] as const,
  wordcloud: (params: { organizationName?: string; limit?: number }) => 
    [...graphQueryKeys.all, 'wordcloud', params] as const,
  explore: (keyword: string) => 
    [...graphQueryKeys.all, 'explore', keyword] as const,
  expand: (params: { nodeId: string; nodeType: string }) =>
    [...graphQueryKeys.all, 'expand', params] as const,
};

/**
 * 워드클라우드 데이터를 조회하는 useQuery 훅
 */
export const useWordCloudQuery = (params: {
  organizationName?: string;
  limit?: number;
}, options?: { enabled?: boolean }) => {
  const { organizationName, limit } = params;
  return useQuery({
    queryKey: graphQueryKeys.wordcloud(params),
    queryFn: () => getWordCloudData({ organizationName, limit }),
    enabled: options?.enabled ?? true, // 기본적으로 활성화
    staleTime: 1000 * 60 * 30, // 30분
  });
};

/**
 * Explore API 데이터를 조회하는 useQuery 훅
 */
export const useExploreQuery = (keyword: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: graphQueryKeys.explore(keyword),
    queryFn: () => getExploreData(keyword),
    enabled: options?.enabled ?? !!keyword, // 키워드가 있을 때만 실행
    staleTime: 1000 * 60 * 5, // 5분
  });
};

/**
 * Expand API 데이터를 조회하는 useQuery 훅 (useQuery가 아닌 useMutation으로 변경 가능)
 * 지금은 일단 useQuery로 구현.
 */
export const useExpandQuery = (params: {
    nodeId: string;
    nodeType: string;
  }, options?: { enabled?: boolean }) => {
  const { nodeId, nodeType } = params;
  return useQuery({
    queryKey: graphQueryKeys.expand(params),
    queryFn: () => getExpandData({ nodeId, nodeType }),
    enabled: options?.enabled ?? false, // 클릭 시에만 실행되도록 기본은 비활성화
    staleTime: 1000 * 60 * 5, // 5분
  });
};