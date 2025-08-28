import { useQuery } from '@tanstack/react-query';
import { getAdminNotices, getAdminNoticeDetail } from '@/services/admin/noticeService';

/**
 * 관리자: 공지사항 관련 쿼리 키
 */
export const adminNoticeQueryKeys = {
  all: ['admin', 'notices'] as const,
  lists: () => [...adminNoticeQueryKeys.all, 'list'] as const,
  details: () => [...adminNoticeQueryKeys.all, 'detail'] as const,
  detail: (id: number | null) => [...adminNoticeQueryKeys.details(), id] as const,
};

/**
 * 관리자: 공지사항 목록을 조회하는 useQuery 훅
 */
export const useAdminNoticesQuery = () => {
  return useQuery({
    queryKey: adminNoticeQueryKeys.lists(),
    queryFn: getAdminNotices,
    staleTime: 1000 * 60 * 3, // 3분
    refetchOnWindowFocus: false,
  });
};

/**
 * 관리자: 특정 공지사항의 상세 정보를 조회하는 useQuery 훅
 */
export const useAdminNoticeDetailQuery = (id: number | null) => {
  return useQuery({
    queryKey: adminNoticeQueryKeys.detail(id),
    queryFn: () => getAdminNoticeDetail(id!),
    enabled: !!id,
  });
};