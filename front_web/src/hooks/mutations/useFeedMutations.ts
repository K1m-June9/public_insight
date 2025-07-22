import { useMutation, useQueryClient } from '@tanstack/react-query';
import {AxiosError} from 'axios'
import { ErrorResponse } from '@/lib/types/base'; 
import { postRating, toggleBookmark } from '@/services/feedService';
import { feedQueryKeys } from '@/hooks/queries/useFeedQueries';
import { userQueryKeys } from '@/hooks/queries/useUserQueries';

/**
 * 피드에 별점을 매기는 useMutation 훅
 */
export const usePostRatingMutation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, score }: { id: number, score: number }) => postRating(id, score),
    onSuccess: (data, variables) => {
      // 별점 매기기 성공 시, 해당 피드의 상세 정보 쿼리를 무효화하여
      // 평균 별점 등을 최신 정보로 다시 불러오게 함
      queryClient.invalidateQueries({ queryKey: feedQueryKeys.detail(variables.id) });
      // 사용자의 별점 목록 쿼리도 무효화
      queryClient.invalidateQueries({ queryKey: userQueryKeys.lists() });
    },
      onError: (error: AxiosError<ErrorResponse>) => {
          const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
          alert(message);
      }
  });
};

/**
 * 피드 북마크를 토글하는 useMutation 훅
 */
export const useToggleBookmarkMutation = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (id: number) => toggleBookmark(id),
        onSuccess: (data, id) => {
            // 북마크 성공 시, 피드 상세 정보와 사용자 북마크 목록 쿼리를 무효화
            queryClient.invalidateQueries({ queryKey: feedQueryKeys.detail(id) });
            queryClient.invalidateQueries({ queryKey: userQueryKeys.bookmarks({}) }); // 북마크 목록 전체 무효화
        },
      onError: (error: AxiosError<ErrorResponse>) => {
          const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
          alert(message);
      }
    });
};