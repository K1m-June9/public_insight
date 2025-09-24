import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as organizationService from '@/services/admin/organizationService';
import { adminOrganizationQueryKeys } from '@/hooks/queries/useAdminOrganizationQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';
import { AdminOrganizationRequest, AdminCategoryCreateRequest, AdminCategoryUpdateRequest } from '@/lib/types/admin/organization';

const useInvalidateOrganizations = () => {
    const queryClient = useQueryClient();
    return () => queryClient.invalidateQueries({ queryKey: adminOrganizationQueryKeys.lists() });
};

// 기관 CRUD
export const useCreateOrganizationMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        // mutationFn이 FormData가 아닌 payload(AdminOrganizationRequest 타입)를 받도록 수정
        mutationFn: (payload: AdminOrganizationRequest) => organizationService.createAdminOrganization(payload),
        onSuccess: () => { alert('기관이 생성되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '기관 생성 실패'); }
    });
};
export const useUpdateOrganizationMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        // FormData 대신 AdminOrganizationRequest payload를 받도록 수정
        mutationFn: ({ id, payload }: { id: number, payload: AdminOrganizationRequest }) => 
            organizationService.updateAdminOrganization(id, payload),
        onSuccess: () => { alert('기관이 수정되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '기관 수정 실패'); }
    });
};
export const useDeleteOrganizationMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        mutationFn: (id: number) => organizationService.deleteAdminOrganization(id),
        onSuccess: () => { alert('기관이 삭제되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '기관 삭제 실패'); }
    });
};

// 카테고리 CRUD
export const useCreateCategoryMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        mutationFn: (payload: AdminCategoryCreateRequest) => organizationService.createAdminCategory(payload),
        onSuccess: () => { alert('카테고리가 생성되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '카테고리 생성 실패'); }
    });
};
export const useUpdateCategoryMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        mutationFn: ({ id, payload }: { id: number, payload: AdminCategoryUpdateRequest }) => organizationService.updateAdminCategory(id, payload),
        onSuccess: () => { alert('카테고리가 수정되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '카테고리 수정 실패'); }
    });
};
export const useDeleteCategoryMutation = () => {
    const invalidate = useInvalidateOrganizations();
    return useMutation({
        mutationFn: (id: number) => organizationService.deleteAdminCategory(id),
        onSuccess: () => { alert('카테고리가 삭제되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '카테고리 삭제 실패'); }
    });
};