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
    feed_count: number;
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

// 백엔드의 WordCloudKeywordItem 스키마에 해당
export interface WordCloudKeywordItem {
  text: string;
  size: number;
  color: string;
  weight: number;
}

// 백엔드의 WordCloudData 스키마에 해당
export interface WordCloudData {
  organization: OrganizationInfo;
  keywords: WordCloudKeywordItem[];
}

// 백엔드의 WordCloudResponse 스키마에 해당
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

// ============================================================================
// 기관 헤더 전용
// ============================================================================
export interface OrganizationStats {
  documents: number;
  views: number;
  satisfaction: number;
}

// 백엔드의 OrganizationSummaryData 스키마에 해당
export interface OrganizationSummaryData {
  id: number;
  name: string;
  description: string;
  website_url?: string;
  stats: OrganizationStats;
}

// 백엔드의 OrganizationSummaryResponse 스키마에 해당
export type OrganizationSummaryResponse = DataResponse<OrganizationSummaryData>;