import { useMutation, useQueryClient } from '@tanstack/react-query';
import * as noticeService from '@/services/admin/noticeService';
import { adminNoticeQueryKeys } from '@/hooks/queries/useAdminNoticeQueries';
import { AxiosError } from 'axios';
import { ErrorResponse } from '@/lib/types/base';
import { AdminNoticeCreateRequest, AdminNoticeUpdateRequest, AdminNoticeStatusUpdateRequest } from '@/lib/types/admin/notice';

const useInvalidateNotices = () => {
    const queryClient = useQueryClient();
    return () => {
        // 목록과 상세 뷰 모두를 무효화하여 최신 상태를 반영
        queryClient.invalidateQueries({ queryKey: adminNoticeQueryKeys.all });
    };
};

// 공지사항 CRUD 뮤테이션 훅
export const useCreateNoticeMutation = () => {
    const invalidate = useInvalidateNotices();
    return useMutation({
        mutationFn: (payload: AdminNoticeCreateRequest) => noticeService.createAdminNotice(payload),
        onSuccess: () => { alert('공지사항이 생성되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '공지사항 생성에 실패했습니다.'); }
    });
};

export const useUpdateNoticeMutation = () => {
    const invalidate = useInvalidateNotices();
    return useMutation({
        mutationFn: ({ id, payload }: { id: number; payload: AdminNoticeUpdateRequest }) => noticeService.updateAdminNotice(id, payload),
        onSuccess: () => { alert('공지사항이 수정되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '공지사항 수정에 실패했습니다.'); }
    });
};

export const useUpdateNoticeStatusMutation = () => {
    const invalidate = useInvalidateNotices();
    return useMutation({
        mutationFn: ({ id, payload }: { id: number; payload: AdminNoticeStatusUpdateRequest }) => noticeService.updateAdminNoticeStatus(id, payload),
        onSuccess: () => { invalidate(); }, // 상태 변경은 사용자에게 alert를 띄우지 않아도 될 수 있음
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '상태 변경에 실패했습니다.'); }
    });
};

export const useDeleteNoticeMutation = () => {
    const invalidate = useInvalidateNotices();
    return useMutation({
        mutationFn: (id: number) => noticeService.deleteAdminNotice(id),
        onSuccess: () => { alert('공지사항이 삭제되었습니다.'); invalidate(); },
        onError: (error: AxiosError<ErrorResponse>) => { alert(error.response?.data.error.message || '공지사항 삭제에 실패했습니다.'); }
    });
};