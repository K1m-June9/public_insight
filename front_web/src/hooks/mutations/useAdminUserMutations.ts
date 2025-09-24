import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as userService from '@/services/admin/userService';
import { adminUserQueryKeys } from '@/hooks/queries/useAdminUserQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';
import { AdminUserRoleChangeRequest, AdminUserStatusChangeRequest } from '@/lib/types/admin/user';

const useInvalidateUsers = () => {
    const queryClient = useQueryClient();
    return (userId?: string) => {
        // 목록 전체를 무효화
        queryClient.invalidateQueries({ queryKey: adminUserQueryKeys.lists() });
        // 특정 유저의 상세 정보가 있다면 그것도 무효화
        if (userId) {
            queryClient.invalidateQueries({ queryKey: adminUserQueryKeys.detail(userId) });
        }
    };
};

export const useUpdateUserRoleMutation = () => {
    const invalidate = useInvalidateUsers();
    return useMutation({
        mutationFn: ({ id, payload }: { id: string; payload: AdminUserRoleChangeRequest }) => userService.updateUserRole(id, payload),
        onSuccess: (_, { id }) => { alert('사용자 역할이 변경되었습니다.'); invalidate(id); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '역할 변경에 실패했습니다.'); }
    });
};

export const useUpdateUserStatusMutation = () => {
    const invalidate = useInvalidateUsers();
    return useMutation({
        mutationFn: ({ id, payload }: { id: string; payload: AdminUserStatusChangeRequest }) => userService.updateUserStatus(id, payload),
        onSuccess: (_, { id }) => { alert('사용자 상태가 변경되었습니다.'); invalidate(id); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '상태 변경에 실패했습니다.'); }
    });
};