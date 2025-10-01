import { apiClient } from '@/lib/api/client';
import {
  AdminUserListResponse,
  AdminUserDetailResponse,
  AdminUserActivityResponse,
  AdminUserRoleChangeResponse,
  AdminUserStatusChangeResponse,
  AdminUserListRequestParams,
  AdminUserRoleChangeRequest,
  AdminUserStatusChangeRequest,
} from '@/lib/types/admin/user';

/**
 * 관리자: 필터링 및 페이지네이션이 적용된 사용자 목록을 조회
 * @param params - 조회 조건 (페이지, 검색어, 역할 등)
 */
export const getAdminUsers = async (params: AdminUserListRequestParams): Promise<AdminUserListResponse> => {
  const response = await apiClient.get<AdminUserListResponse>('/admin/users', { params });
  return response.data;
};

/**
 * 관리자: ID로 특정 사용자의 상세 정보를 조회
 * @param id - 조회할 사용자의 user_id (문자열)
 */
export const getAdminUserDetail = async (id: string): Promise<AdminUserDetailResponse> => {
  const response = await apiClient.get<AdminUserDetailResponse>(`/admin/users/${id}`);
  return response.data;
};

/**
 * 관리자: ID로 특정 사용자의 활동 로그를 조회
 * @param id - 조회할 사용자의 user_id (문자열)
 * @param params - 페이지네이션 정보
 */
export const getAdminUserActivities = async (id: string, params: { page?: number; limit?: number }): Promise<AdminUserActivityResponse> => {
  const response = await apiClient.get<AdminUserActivityResponse>(`/admin/users/${id}/activities`, { params });
  return response.data;
};

/**
 * 관리자: 특정 사용자의 역할을 변경
 * @param id - 변경할 사용자의 user_id (문자열)
 * @param payload - 새로운 역할 정보
 */
export const updateUserRole = async (id: string, payload: AdminUserRoleChangeRequest): Promise<AdminUserRoleChangeResponse> => {
  const response = await apiClient.patch<AdminUserRoleChangeResponse>(`/admin/users/${id}/role`, payload);
  return response.data;
};

/**
 * 관리자: 특정 사용자의 상태를 변경
 * @param id - 변경할 사용자의 user_id (문자열)
 * @param payload - 새로운 상태 정보
 */
export const updateUserStatus = async (id: string, payload: AdminUserStatusChangeRequest): Promise<AdminUserStatusChangeResponse> => {
  const response = await apiClient.patch<AdminUserStatusChangeResponse>(`/admin/users/${id}/status`, payload);
  return response.data;
};