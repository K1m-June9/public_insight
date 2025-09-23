import { useMutation } from '@tanstack/react-query';
import { getExpandData } from '@/services/graphService';

/**
 * Expand API를 호출하여 그래프를 확장하는 useMutation 훅
 */
export const useExpandMutation = () => {
  return useMutation({
    mutationFn: getExpandData,
    onSuccess: (data) => {
      console.log('Graph expansion successful:', data);
    },
    onError: (error) => {
      console.error('Graph expansion failed:', error);
    },
  });
};