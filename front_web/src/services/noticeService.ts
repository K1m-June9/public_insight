import { apiClient } from '@/lib/api/client';
import { 
    PinnedNoticeResponse,
    NoticeListResponse,
    NoticeDetailResponse
} from '@/lib/types/notice';

interface PaginationParams {
    page?: number;
    limit?: number;
}

/**
* 고정된 공지사항 목록을 조회합니다.
* @returns Promise<PinnedNoticeResponse>
*/
export const getPinnedNotices = async (): Promise<PinnedNoticeResponse> => {
    const response = await apiClient.get<PinnedNoticeResponse>('/notices/pinned');
    return response.data;
};

/**
* 전체 공지사항 목록을 페이지네이션하여 조회합니다.
* @param params - 페이지네이션 파라미터 (page, limit)
* @returns Promise<NoticeListResponse>
*/
export const getNotices = async (params: PaginationParams): Promise<NoticeListResponse> => {
    // 백엔드 라우터가 "/" 이므로, prefix인 "/notices" 만으로 요청합니다.
    const response = await apiClient.get<NoticeListResponse>('/notices', { params });
    return response.data;
};

/**
* 특정 공지사항의 상세 정보를 조회합니다.
* @param id - 공지사항의 고유 ID
* @returns Promise<NoticeDetailResponse>
*/
export const getNoticeDetail = async (id: number): Promise<NoticeDetailResponse> => {
    const response = await apiClient.get<NoticeDetailResponse>(`/notices/${id}`);
    return response.data;
};