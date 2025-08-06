import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateAdminFeed } from '@/services/admin/feedService';
import { AdminFeedUpdateRequest } from '@/lib/types/admin/feed';
import { adminFeedQueryKeys } from '@/hooks/queries/useAdminFeedQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';

/**
 * 관리자: 피드 정보를 수정하는 useMutation 훅
 */
export const useUpdateAdminFeedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: AdminFeedUpdateRequest }) => 
      updateAdminFeed(id, payload),
    
    onSuccess: (data, variables) => {
      alert('피드 정보가 성공적으로 수정되었습니다.');

      // 수정 성공 시, 관련된 목록과 상세 정보 쿼리를 모두 무효화하여 자동 갱신
      queryClient.invalidateQueries({ queryKey: adminFeedQueryKeys.lists() });
      queryClient.invalidateQueries({ queryKey: adminFeedQueryKeys.detail(variables.id) });
    },
    
    onError: (error: AxiosError<ErrorResponse>) => {
      const message = error.response?.data?.error?.message || '피드 수정 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};