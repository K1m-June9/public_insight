import { useMutation, useQueryClient } from '@tanstack/react-query';
import { updateNickname, updatePassword } from '@/services/userService';
import { userQueryKeys } from '@/hooks/queries/useUserQueries';

/**
 * 닉네임 변경을 위한 useMutation 훅
 */
export const useUpdateNicknameMutation = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newNickname: string) => updateNickname(newNickname),
    onSuccess: (data) => {
      // 닉네임 변경 성공 시, '내 정보' 쿼리를 무효화하여 최신 정보로 다시 불러오게 함
      queryClient.invalidateQueries({ queryKey: userQueryKeys.me() });
      alert('닉네임이 성공적으로 변경되었습니다.');
      // 또는, 서버 응답 데이터로 직접 캐시를 업데이트할 수도 있음
      // queryClient.setQueryData(userQueryKeys.me(), data);
    },
    onError: (error: any) => {
      const message = error.response?.data?.error?.message || '닉네임 변경 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};

/**
 * 비밀번호 변경을 위한 useMutation 훅
 */
export const useUpdatePasswordMutation = () => {
  return useMutation({
    mutationFn: (params: { current_password: string; new_password: string }) => updatePassword(params),
    onSuccess: () => {
      alert('비밀번호가 성공적으로 변경되었습니다.');
      // 필요 시 로그아웃 처리 또는 다른 로직 수행
    },
    onError: (error: any) => {
      const message = error.response?.data?.error?.message || '비밀번호 변경 중 오류가 발생했습니다.';
      alert(message);
    }
  });
};