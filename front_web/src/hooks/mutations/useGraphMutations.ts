import { useMutation, type UseMutationOptions } from '@tanstack/react-query';
import { getExpandData } from '@/services/graphService';
import { GraphResponse } from '@/lib/types/graph';
import { ErrorResponse } from '@/lib/types/base';
/**
 * Expand API를 호출하여 그래프를 확장하는 useMutation 훅
 */
export const useExpandMutation = (
  options?: UseMutationOptions<
    GraphResponse,      // 성공 시 반환될 데이터(TData)의 타입
    ErrorResponse,      // 실패 시 반환될 에러(TError)의 타입
    { nodeId: string; nodeType: string } // mutate 함수에 전달될 변수(TVariables)의 타입
  >
) => {
  return useMutation({
    mutationFn: getExpandData,
    onSuccess: (data) => {
      console.log('Graph expansion successful:', data);
    },
    onError: (error) => {
      console.error('Graph expansion failed:', error);
    },
    ...options,
  });
};