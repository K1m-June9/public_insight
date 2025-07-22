import { useQuery } from '@tanstack/react-query';
import { getPinnedNotices, getNotices, getNoticeDetail } from '@/services/noticeService';

interface PaginationParams {
    page?: number;
    limit?: number;
}

// 공지사항 관련 쿼리 키를 관리하는 객체
export const noticeQueryKeys = {
  all: ['notices'] as const,
  lists: () => [...noticeQueryKeys.all, 'list'] as const,
  list: (params: PaginationParams) => [...noticeQueryKeys.lists(), params] as const,
  pinned: () => [...noticeQueryKeys.all, 'pinned'] as const,
  details: () => [...noticeQueryKeys.all, 'detail'] as const,
  detail: (id: number) => [...noticeQueryKeys.details(), id] as const,
};

/**
 * 고정된 공지사항 목록을 조회하는 useQuery 훅
 * 
 * @param options - useQuery에 전달할 추가 옵션
 * @returns {data, isLoading, ...}
 */
export const usePinnedNoticesQuery = (options?: { staleTime?: number }) => {
  return useQuery({
    queryKey: noticeQueryKeys.pinned(),
    queryFn: () => getPinnedNotices(),
    staleTime: options?.staleTime ?? 1000 * 60 * 5, // 5분
  });
};

/**
 * 전체 공지사항 목록을 페이지네이션하여 조회하는 useQuery 훅
 * 
 * @param params - 페이지네이션 파라미터 (page, limit)
 * @returns {data, isLoading, ...}
 */
export const useNoticesQuery = (params: PaginationParams) => {
  return useQuery({
    queryKey: noticeQueryKeys.list(params),
    queryFn: () => getNotices(params),
    placeholderData: (previousData) => previousData, // 페이지 이동 시 이전 데이터 유지
  });
};

/**
 * 특정 공지사항의 상세 정보를 조회하는 useQuery 훅
 * 
 * @param id - 조회할 공지사항의 ID
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled)
 * @returns {data, isLoading, ...}
 */
export const useNoticeDetailQuery = (id: number, options?: { enabled?: boolean }) => {
  return useQuery({
    queryKey: noticeQueryKeys.detail(id),
    queryFn: () => getNoticeDetail(id),
    enabled: options?.enabled ?? !!id, // id가 유효한 값일 때만 쿼리 실행
    staleTime: 1000 * 60 * 5, // 5분
  });
};