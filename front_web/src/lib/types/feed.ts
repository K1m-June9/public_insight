import { BaseResponse, DataResponse, PaginationInfo } from './base';
import { OrganizationInfo } from './organization';

// ============================================================================
// 공통 정보
// ============================================================================

export interface CategoryInfo {
    id: number;
    name: string;
}

// ============================================================================
// 1. 메인 페이지 피드 목록
// ============================================================================

export interface MainFeedItem {
    id: number;
    title: string;
    organization: OrganizationInfo;
    summary: string;
    published_date: string; // 시간은 string으로 (ISO 8601)
    view_count: number;
    average_rating: number;
}

export interface MainFeedListData {
    feeds: MainFeedItem[];
    pagination: PaginationInfo;
}

export type MainFeedListResponse = DataResponse<MainFeedListData>;

// ============================================================================
// 2. 기관 페이지 피드 목록
// ============================================================================

export interface OrganizationFeedItem {
    id: number;
    title: string;
    category: CategoryInfo;
    summary: string;
    published_date: string;
    view_count: number;
    average_rating: number;
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

// ============================================================================
// 5. 피드 상세
// ============================================================================

export interface FeedDetail {
    id: number;
    title: string;
    organization: OrganizationInfo;
    category: CategoryInfo;
    average_rating: number;
    view_count: number;
    published_date: string;
    content: string; // HTML 또는 Markdown 문자열
    source_url: string;
}

export interface FeedDetailData {
    feed: FeedDetail;
}

export type FeedDetailResponse = DataResponse<FeedDetailData>;

// ============================================================================
// 6. 북마크 및 별점
// ============================================================================

export interface BookmarkData {
    is_bookmarked: boolean;
    bookmark_count: number;
    message: string;
}
export type BookmarkResponse = DataResponse<BookmarkData>;

export interface RatingData {
    user_rating: number;
    average_rating: number;
    total_ratings: number;
    message: string;
}
export type RatingResponse = DataResponse<RatingData>;