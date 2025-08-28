import { BaseResponse, DataResponse } from '@/lib/types/base';

/**
 * 관리자: 공지사항 목록의 각 항목에 대한 타입
 */
export interface AdminNoticeListItem {
  id: number;
  title: string;
  author: string;
  is_pinned: boolean;
  is_active: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
}

/**
 * 관리자: 공지사항 상세 정보 타입
 */
export interface AdminNoticeDetail {
  id: number;
  title: string;
  content: string;
  author: string;
  is_pinned: boolean;
  is_active: boolean;
  view_count: number;
  created_at: string;
  updated_at: string | null;
}

/** 관리자: 공지사항 생성 요청 Body 타입 */
export interface AdminNoticeCreateRequest {
  title: string;
  content: string;
  is_active: boolean;
}

/** 관리자: 공지사항 수정 요청 Body 타입 (전체 수정) */
export interface AdminNoticeUpdateRequest {
  title: string;
  content: string;
  is_active: boolean;
}

/** 관리자: 공지사항 상태(고정/활성) 수정 요청 Body 타입 (부분 수정) */
export interface AdminNoticeStatusUpdateRequest {
  is_pinned?: boolean;
  is_active?: boolean;
}

/** 관리자: 공지사항 목록 조회 API 응답 타입 */
export type AdminNoticeListResponse = DataResponse<AdminNoticeListItem[]>;
/** 관리자: 공지사항 상세 조회/생성/수정 API 응답 타입 */
export type AdminNoticeResponse = DataResponse<AdminNoticeDetail>;
/** 관리자: 공지사항 삭제 API 응답 타입 */
export type AdminNoticeDeleteResponse = BaseResponse & { message: string };