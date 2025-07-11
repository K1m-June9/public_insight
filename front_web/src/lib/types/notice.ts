import { DataResponse, PaginationInfo } from './base';

// =================================
// 1. 고정 공지사항 관련
// =================================

export interface PinnedNoticeItem {
    id: number;
    title: string;
    created_at: string;
}

export interface PinnedNoticeData {
    notices: PinnedNoticeItem[];
    count: number;
}

export type PinnedNoticeResponse = DataResponse<PinnedNoticeData>;

// =================================
// 2. 공지사항 목록 관련
// =================================

export interface NoticeListItem {
    id: number;
    title: string;
    author: string;
    is_pinned: boolean;
    created_at: string;
}

export interface NoticeListData {
    notices: NoticeListItem[];
    pagination: PaginationInfo;
}

export type NoticeListResponse = DataResponse<NoticeListData>;

// =================================
// 3. 공지사항 상세 관련
// =================================

export interface NoticeDetail {
    id: number;
    title: string;
    author: string;
    content: string;
    is_pinned: boolean;
    view_count: number;
    created_at: string;
    updated_at?: string;
}

export interface NoticeDetailData {
    notice: NoticeDetail;
}

export type NoticeDetailResponse = DataResponse<NoticeDetailData>;