import { DataResponse } from './base';

// =================================
// 1. 슬라이더 목록 관련
// =================================

export interface SliderListItem {
    id: number;
    title: string;
    preview: string;
    image: string; // Base64 인코딩된 이미지 데이터
    display_order: number;
}

export interface SliderListData {
    sliders: SliderListItem[];
}

export type SliderListResponse = DataResponse<SliderListData>;

// =================================
// 2. 슬라이더 상세 관련
// =================================

export interface SliderDetail {
    id: number;
    title: string;
    content: string;
    image: string; // Base64 인코딩된 이미지 데이터
    author: string;
    tag: string;
    created_at: string;
}

export interface SliderDetailData {
    slider: SliderDetail;
}

export type SliderDetailResponse = DataResponse<SliderDetailData>;