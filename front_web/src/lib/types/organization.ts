import { DataResponse } from './base';

// ============================================================================
// 1. 기관 목록 관련
// ============================================================================

export interface OrganizationListItem {
    id: number;
    name: string;
    percentage: number;
}

export interface OrganizationListData {
    organizations: OrganizationListItem[];
    total_percentage: number;
}

export type OrganizationListResponse = DataResponse<OrganizationListData>;

// ============================================================================
// 2. 기관별 카테고리 관련
// ============================================================================

export interface OrganizationInfo {
    id: number;
    name: string;
}

export interface CategoryItem {
    id: number;
    name: string;
    percentage: number;
}

export interface OrganizationCategoryData {
    organization: OrganizationInfo;
    categories: CategoryItem[];
    total_percentage: number;
}

export type OrganizationCategoryResponse = DataResponse<OrganizationCategoryData>;


// ============================================================================
// 3. 워드클라우드 관련
// ============================================================================

export interface WordItem {
    text: string;
    value: number;
}

export interface WordCloudPeriod {
    start_date: string; // 날짜는 string으로 받는 것이 편리(YYYY-MM-DD)
    end_date: string;
}

export interface WordCloudByYear {
    year: number;
    words: WordItem[];
    period: WordCloudPeriod;
    generated_at: string; // 시간도 string으로 받는 것이 편리(ISO 8601)
}

export interface WordCloudData {
    organization: OrganizationInfo;
    wordclouds: WordCloudByYear[];
}

export type WordCloudResponse = DataResponse<WordCloudData>;

// ============================================================================
// 4. 기관 아이콘 관련
//    나중에 삭제할거지만 지금 당장은 쓸 타입
//    시₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩₩발
// ============================================================================

export interface OrganizationWithIcon {
    id: number;
    name: string;
    website_url: string; //기관 웹사이트 url
    iconUrl: string;
}

export interface OrganizationIconData {
    organization: OrganizationWithIcon;
}

export type OrganizationIconResponse = DataResponse<OrganizationIconData>;