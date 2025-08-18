import { DataResponse } from './base';

// =================================
// 1. 슬라이더 목록 관련
// =================================

export interface SliderListItem {
    id: number;
    title: string;
    preview: string;
    imageUrl: string; 
    display_order: number;
    created_at: string;
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
    imageUrl: string; 
    author: string;
    tag: string;
    created_at: string;
}

export interface SliderDetailData {
    slider: SliderDetail;
}

export type SliderDetailResponse = DataResponse<SliderDetailData>;