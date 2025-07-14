import { useQuery } from '@tanstack/react-query';
import { getSliders, getSliderDetail } from '@/services/sliderService';

// 슬라이더 관련 쿼리 키를 관리하는 객체
export const sliderQueryKeys = {
  all: ['sliders'] as const,
  lists: () => [...sliderQueryKeys.all, 'list'] as const,
  list: (params: any) => [...sliderQueryKeys.lists(), params] as const, // 목록 쿼리는 파라미터를 포함할 수 있음
  details: () => [...sliderQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...sliderQueryKeys.details(), id] as const,
};

/**
 * 메인 페이지에 표시될 슬라이더 목록을 조회하는 useQuery 훅
 * 
 * @param options - useQuery에 전달할 추가 옵션
 * @returns {data, isLoading, ...}
 */
export const useSlidersQuery = (options?: { staleTime?: number }) => {
  return useQuery({
    queryKey: sliderQueryKeys.lists(),
    queryFn: () => getSliders(),
    staleTime: options?.staleTime ?? 1000 * 60 * 5, // 기본 5분, 슬라이더는 자주 바뀌지 않으므로(아마도)
  });
};

/**
 * 특정 슬라이더의 상세 정보를 조회하는 useQuery 훅
 * 
 * @param id - 조회할 슬라이더의 ID
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useSliderDetailQuery = (id: number, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: sliderQueryKeys.detail(id),
    queryFn: () => getSliderDetail(id),
    enabled: options?.enabled ?? !!id, // id가 유효한(0이 아닌) 값일 때만 쿼리 실행
    staleTime: 1000 * 60 * 1, // 기본 1분
  });
};