import { apiClient } from '@/lib/api/client';
import {
  AdminSliderListResponse,
  AdminSliderResponse,
  AdminSliderStatusUpdateResponse,
  AdminSliderDeleteResponse,
  AdminSliderStatusUpdateRequest,
} from '@/lib/types/admin/slider';

/**
 * 관리자: 모든 슬라이더 목록을 조회
 */
export const getAdminSliders = async (): Promise<AdminSliderListResponse> => {
  const response = await apiClient.get<AdminSliderListResponse>('/admin/slider');
  return response.data;
};

/**
 * 관리자: ID로 특정 슬라이더의 상세 정보를 조회
 */
export const getAdminSliderDetail = async (id: number): Promise<AdminSliderResponse> => {
  const response = await apiClient.get<AdminSliderResponse>(`/admin/slider/${id}`);
  return response.data;
};

/**
 * 관리자: 새로운 슬라이더를 생성 (파일 업로드 포함)
 * @param formData - 텍스트 필드와 이미지 파일(optional)을 포함하는 FormData
 */
export const createAdminSlider = async (formData: FormData): Promise<AdminSliderResponse> => {
  const response = await apiClient.post<AdminSliderResponse>('/admin/slider', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * 관리자: 기존 슬라이더의 정보를 수정 (파일 업로드 포함)
 * @param id - 수정할 슬라이더의 ID
 * @param formData - 수정할 텍스트 필드와 이미지 파일(optional)을 포함하는 FormData
 */
export const updateAdminSlider = async (id: number, formData: FormData): Promise<AdminSliderResponse> => {
  const response = await apiClient.put<AdminSliderResponse>(`/admin/slider/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

/**
 * 관리자: 기존 슬라이더의 활성화 상태를 수정
 */
export const updateAdminSliderStatus = async (id: number, payload: AdminSliderStatusUpdateRequest): Promise<AdminSliderStatusUpdateResponse> => {
  const response = await apiClient.patch<AdminSliderStatusUpdateResponse>(`/admin/slider/${id}`, payload);
  return response.data;
};

/**
 * 관리자: 특정 슬라이더를 삭제
 */
export const deleteAdminSlider = async (id: number): Promise<AdminSliderDeleteResponse> => {
  const response = await apiClient.delete<AdminSliderDeleteResponse>(`/admin/slider/${id}`);
  return response.data;
};