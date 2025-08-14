import { DataResponse, PaginationInfo } from './base';
import { OrganizationInfo } from './organization';

// =================================
// 공통 정보
// =================================

export interface CategoryInfo {
    id: number;
    name: string;
}

// =================================
// 1. 메인 페이지 피드 목록
// =================================

export interface MainFeedItem {
    id: number;
    title: string;
    organization: OrganizationInfo;
    summary: string;
    published_date: string;
    view_count: number;
    average_rating: number;
    bookmark_count: number;
}

export interface MainFeedListData {
    feeds: MainFeedItem[];
    pagination: PaginationInfo;
}

export type MainFeedListResponse = DataResponse<MainFeedListData>;

// =================================
// 2. 기관 페이지 피드 목록
// =================================

export interface OrganizationFeedItem {
    id: number;
    title: string;
    category: CategoryInfo;
    summary: string;
    published_date: string;
    view_count: number;
    average_rating: number;
    bookmark_count: number;
}

export interface FeedFilter {
    category_id: number;
    category_name: string;
}

export interface OrganizationFeedListData {
    organization: OrganizationInfo;
    feeds: OrganizationFeedItem[];
    pagination: PaginationInfo;
    filter?: FeedFilter;
}

export type OrganizationFeedListResponse = DataResponse<OrganizationFeedListData>;

// =================================
// 3. 최신 피드 슬라이드
// =================================

export interface LatestFeedItem {
    id: number;
    title: string;
    organization: OrganizationInfo;
}

export interface LatestFeedData {
    feeds: LatestFeedItem[];
    count: number;
}

export type LatestFeedResponse = DataResponse<LatestFeedData>;

export interface OrganizationLatestFeedItem {
    id: number;
    title: string;
    category: CategoryInfo;
}

export interface OrganizationLatestFeedData {
    organization: OrganizationInfo;
    feeds: OrganizationLatestFeedItem[];
    count: number;
}

export type OrganizationLatestFeedResponse = DataResponse<OrganizationLatestFeedData>;

// =================================
// 4. TOP5 피드 (누락되었던 부분)
// =================================

export interface Top5FeedItem {
    id: number;
    title: string;
    organization: string;
    average_rating: number;
    view_count: number;
    bookmark_count: number;
}

export interface Top5FeedData {
    top_rated: Top5FeedItem[];
    most_viewed: Top5FeedItem[];
    most_bookmarked: Top5FeedItem[];
}

export type Top5FeedResponse = DataResponse<Top5FeedData>;

// =================================
// 5. 보도자료
// =================================

export interface PressReleaseItem {
    id: number;
    title: string;
    category: CategoryInfo;
    summary: string;
    published_date: string;
    view_count: number;
    average_rating: number;
}

export interface PressReleaseData {
    organization: OrganizationInfo;
    press_releases: PressReleaseItem[];
    pagination: PaginationInfo;
}

export type PressReleaseResponse = DataResponse<PressReleaseData>;

// =================================
// 6. 피드 상세
// =================================

export interface FeedDetail {
    id: number;
    title: string;
    organization: OrganizationInfo;
    category: CategoryInfo;
    average_rating: number;
    view_count: number;
    published_date: string;
    source_url: string;

    pdf_url: string; //PDF 자체
    is_bookmarked?: boolean; // 로그인 시에만 오므로 optional '?' 처리
    user_rating?: number;    // 로그인 시에만 오므로 optional '?' 처리
}

export interface FeedDetailData {
    feed: FeedDetail;
}

export type FeedDetailResponse = DataResponse<FeedDetailData>;

// =================================
// 7. 북마크 및 별점
// =================================

export interface BookmarkData {
    is_bookmarked: boolean;
    bookmark_count: number;
    message: string;
}
export type BookmarkResponse = DataResponse<BookmarkData>;

export interface RatingData {
    user_rating: number;
    average_rating: number;
    total_ratings: number; // 스키마에 int로 되어있어 number로 변경
    message: string;
}
export type RatingResponse = DataResponse<RatingData>;