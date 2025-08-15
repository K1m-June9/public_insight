import { useQuery } from '@tanstack/react-query';
import {
    getOrganizationsForChart,
    getOrganizationCategoriesForChart,
    getOrganizationWordCloud,
    getOrganizationIcon,
    getOrganizationSummary
} from '@/services/organizationService';

// 기관 관련 쿼리 키를 관리하는 객체
export const organizationQueryKeys = {
  all: ['organizations'] as const,
  lists: () => [...organizationQueryKeys.all, 'list'] as const,
  list: (params: any) => [...organizationQueryKeys.lists(), params] as const, // 예시
  details: () => [...organizationQueryKeys.all, 'detail'] as const,
  detail: (name: string) => [...organizationQueryKeys.details(), name] as const,
  categories: (name: string) => [...organizationQueryKeys.detail(name), 'categories'] as const,
  wordcloud: (name: string) => [...organizationQueryKeys.detail(name), 'wordcloud'] as const,
  icon: (name: string) => [...organizationQueryKeys.detail(name), 'icon'] as const,
  summary: (name: string) => [...organizationQueryKeys.detail(name), 'summary'] as const,
};

/**
 * 메인 페이지 원형 그래프에 사용될 기관 목록을 조회하는 useQuery 훅
 * 
 * @param options - useQuery에 전달할 추가 옵션
 * @returns {data, isLoading, ...}
 */
export const useOrganizationsForChartQuery = (options?: { staleTime?: number }) => {
  return useQuery({
    queryKey: organizationQueryKeys.lists(),
    queryFn: getOrganizationsForChart,
    staleTime: options?.staleTime ?? 1000 * 60 * 10, // 10분. 기관 목록은 자주 변하지 않음.
  });
};

/**
 * 특정 기관의 카테고리 목록과 비율을 조회하는 useQuery 훅
 * 
 * @param name - 조회할 기관의 이름
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useOrganizationCategoriesForChartQuery = (name: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: organizationQueryKeys.categories(name),
    queryFn: () => getOrganizationCategoriesForChart(name),
    enabled: options?.enabled ?? !!name,
    staleTime: 1000 * 60 * 10, // 10분
  });
};

/**
 * 특정 기관의 워드클라우드 데이터를 조회하는 useQuery 훅
 * 
 * @param name - 조회할 기관의 이름
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useOrganizationWordCloudQuery = (name: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: organizationQueryKeys.wordcloud(name),
    queryFn: () => getOrganizationWordCloud(name),
    enabled: options?.enabled ?? !!name,
    staleTime: 1000 * 60 * 30, // 30분. 워드클라우드는 더더욱 자주 변하지 않음.
  });
};

/**
 * 특정 기관의 아이콘(Base64)을 조회하는 useQuery 훅
 * 
 * @param name - 조회할 기관의 이름
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useOrganizationIconQuery = (name: string, options?: { enabled?: boolean }) => {
    return useQuery({
      queryKey: organizationQueryKeys.icon(name),
      queryFn: () => getOrganizationIcon(name),
      enabled: options?.enabled ?? !!name,
      staleTime: Infinity, // 아이콘은 절대 변하지 않는다고 가정하고, 캐시를 영구적으로 유지(나중에 API 호출 방식에서 변경하면 이거도 다시 바꿀 예정)
    });
};

/**
 * 특정 기관의 요약 정보를 조회하는 useQuery 훅
 * 
 * @param name - 조회할 기관의 이름
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useOrganizationSummaryQuery = (name: string, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: organizationQueryKeys.summary(name),
    queryFn: () => getOrganizationSummary(name),
    enabled: options?.enabled ?? !!name,
    // 기관 요약 정보는 자주 바뀌지 않으므로 staleTime을 길게 설정
    staleTime: 1000 * 60 * 10, // 10분
  });
};