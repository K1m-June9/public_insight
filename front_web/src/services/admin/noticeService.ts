import { apiClient } from '@/lib/api/client';
import {
  AdminNoticeListResponse,
  AdminNoticeResponse,
  AdminNoticeDeleteResponse,
  AdminNoticeCreateRequest,
  AdminNoticeUpdateRequest,
  AdminNoticeStatusUpdateRequest,
} from '@/lib/types/admin/notice';

/**
 * 관리자: 모든 공지사항 목록을 조회
 */
export const getAdminNotices = async (): Promise<AdminNoticeListResponse> => {
  const response = await apiClient.get<AdminNoticeListResponse>('/admin/notices');
  return response.data;
};

/**
 * 관리자: ID로 특정 공지사항의 상세 정보를 조회
 */
export const getAdminNoticeDetail = async (id: number): Promise<AdminNoticeResponse> => {
  const response = await apiClient.get<AdminNoticeResponse>(`/admin/notices/${id}`);
  return response.data;
};

/**
 * 관리자: 새로운 공지사항을 생성
 */
export const createAdminNotice = async (payload: AdminNoticeCreateRequest): Promise<AdminNoticeResponse> => {
  const response = await apiClient.post<AdminNoticeResponse>('/admin/notices', payload);
  return response.data;
};

/**
 * 관리자: 기존 공지사항의 전체 내용을 수정 (PUT)
 */
export const updateAdminNotice = async (id: number, payload: AdminNoticeUpdateRequest): Promise<AdminNoticeResponse> => {
  const response = await apiClient.put<AdminNoticeResponse>(`/admin/notices/${id}`, payload);
  return response.data;
};

/**
 * 관리자: 기존 공지사항의 상태(고정/활성)를 수정 (PATCH)
 */
export const updateAdminNoticeStatus = async (id: number, payload: AdminNoticeStatusUpdateRequest): Promise<AdminNoticeResponse> => {
  const response = await apiClient.patch<AdminNoticeResponse>(`/admin/notices/${id}`, payload);
  return response.data;
};

/**
 * 관리자: 특정 공지사항을 삭제
 */
export const deleteAdminNotice = async (id: number): Promise<AdminNoticeDeleteResponse> => {
  const response = await apiClient.delete<AdminNoticeDeleteResponse>(`/admin/notices/${id}`);
  return response.data;
};