import { useQuery } from '@tanstack/react-query';
import { getAdminSliders, getAdminSliderDetail } from '@/services/admin/sliderService';

/**
 * 관리자: 슬라이더 관련 쿼리 키
 */
export const adminSliderQueryKeys = {
  all: ['admin', 'sliders'] as const,
  lists: () => [...adminSliderQueryKeys.all, 'list'] as const,
  details: () => [...adminSliderQueryKeys.all, 'detail'] as const,
  detail: (id: number | null) => [...adminSliderQueryKeys.details(), id] as const,
};

/**
 * 관리자: 슬라이더 목록을 조회하는 useQuery 훅
 */
export const useAdminSlidersQuery = () => {
  return useQuery({
    queryKey: adminSliderQueryKeys.lists(),
    queryFn: getAdminSliders,
    staleTime: 1000 * 60 * 5, // 5분
    refetchOnWindowFocus: false,
  });
};

/**
 * 관리자: 특정 슬라이더의 상세 정보를 조회하는 useQuery 훅
 */
export const useAdminSliderDetailQuery = (id: number | null) => {
  return useQuery({
    queryKey: adminSliderQueryKeys.detail(id),
    queryFn: () => getAdminSliderDetail(id!),
    enabled: !!id,
  });
};