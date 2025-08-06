import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateAdminFeed, createAdminFeed, deleteAdminFeed } from '@/services/admin/feedService';
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

/**
 * 관리자: 새로운 피드를 생성하는 useMutation 훅
 */
export const useCreateAdminFeedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => createAdminFeed(formData),
    
    onSuccess: (data) => {
      alert('피드 생성 요청이 접수되었습니다.');

      // 생성 요청이 성공하면, 피드 목록을 다시 불러와 'processing' 상태를 보여줌
      queryClient.invalidateQueries({ queryKey: adminFeedQueryKeys.lists() });
    },
    
    onError: (error: AxiosError<ErrorResponse>) => {
      const message = error.response?.data?.error?.message || '피드 생성 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};

export const useDeleteAdminFeedMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteAdminFeed(id),
    onSuccess: () => {
      alert('피드가 완전히 삭제되었습니다.');
      // 비활성화된 피드 목록 쿼리를 무효화하여 자동 갱신
      queryClient.invalidateQueries({ queryKey: adminFeedQueryKeys.deactivatedLists() });
    },
    onError: (error: AxiosError<ErrorResponse>) => {
      const message = error.response?.data?.error?.message || '피드 삭제 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};