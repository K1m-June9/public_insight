import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateAdminStaticPage } from '@/services/admin/staticPageService';
import { AdminStaticPageUpdateRequest } from '@/lib/types/admin/staticPage';
import { adminStaticPageQueryKeys } from '@/hooks/queries/useAdminStaticPageQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';

/**
 * 관리자: 정적 페이지 내용을 수정하는 useMutation 훅
 */
export const useUpdateAdminStaticPageMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ slug, payload }: { slug: string; payload: AdminStaticPageUpdateRequest }) => 
      updateAdminStaticPage(slug, payload),
    
    onSuccess: (data, variables) => {
      // 수정 성공 시
      alert('페이지 내용이 성공적으로 저장되었습니다.');

      // 관련된 쿼리들을 무효화하여 최신 데이터로 갱신하도록 함
      // 1. 목록 쿼리 무효화
      queryClient.invalidateQueries({ queryKey: adminStaticPageQueryKeys.lists() });
      // 2. 이 특정 페이지의 상세 정보 쿼리 무효화
      queryClient.invalidateQueries({ queryKey: adminStaticPageQueryKeys.detail(variables.slug) });
    },
    
    onError: (error: AxiosError<ErrorResponse>) => {
      // 수정 실패 시
      const message = error.response?.data?.error?.message || '페이지 저장 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};