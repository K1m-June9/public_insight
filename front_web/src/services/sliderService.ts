import { apiClient } from '@/lib/api/client';
import { SliderListResponse, SliderDetailResponse } from '@/lib/types/slider';

/**
* 메인 페이지에 표시될 활성화된 슬라이더 목록을 조회
* @returns Promise<SliderListResponse>
*/
export const getSliders = async (): Promise<SliderListResponse> => {
    const response = await apiClient.get<SliderListResponse>('/sliders');
    return response.data;
};

/**
* 특정 슬라이더의 상세 정보를 조회(슬라이더 상세 페이지)
* @param id - 슬라이더의 고유 ID
* @returns Promise<SliderDetailResponse>
*/
export const getSliderDetail = async (id: number): Promise<SliderDetailResponse> => {
    const response = await apiClient.get<SliderDetailResponse>(`/sliders/${id}`);
    return response.data;
};