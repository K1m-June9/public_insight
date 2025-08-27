import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as sliderService from '@/services/admin/sliderService';
import { adminSliderQueryKeys } from '@/hooks/queries/useAdminSliderQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';
import { AdminSliderStatusUpdateRequest } from '@/lib/types/admin/slider';

const useInvalidateSliders = () => {
    const queryClient = useQueryClient();
    return () => {
        queryClient.invalidateQueries({ queryKey: adminSliderQueryKeys.all });
    };
};

// 슬라이더 CRUD 뮤테이션 훅
export const useCreateSliderMutation = () => {
    const invalidate = useInvalidateSliders();
    return useMutation({
        mutationFn: (formData: FormData) => sliderService.createAdminSlider(formData),
        onSuccess: () => { alert('슬라이더가 생성되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '슬라이더 생성에 실패했습니다.'); }
    });
};

export const useUpdateSliderMutation = () => {
    const invalidate = useInvalidateSliders();
    return useMutation({
        mutationFn: ({ id, formData }: { id: number; formData: FormData }) => sliderService.updateAdminSlider(id, formData),
        onSuccess: () => { alert('슬라이더가 수정되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '슬라이더 수정에 실패했습니다.'); }
    });
};

export const useUpdateSliderStatusMutation = () => {
    const invalidate = useInvalidateSliders();
    return useMutation({
        mutationFn: ({ id, payload }: { id: number; payload: AdminSliderStatusUpdateRequest }) => sliderService.updateAdminSliderStatus(id, payload),
        onSuccess: () => { invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '상태 변경에 실패했습니다.'); }
    });
};

export const useDeleteSliderMutation = () => {
    const invalidate = useInvalidateSliders();
    return useMutation({
        mutationFn: (id: number) => sliderService.deleteAdminSlider(id),
        onSuccess: () => { alert('슬라이더가 삭제되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '슬라이더 삭제에 실패했습니다.'); }
    });
};