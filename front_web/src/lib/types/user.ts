import { DataResponse, PaginationInfo, UserRole } from './base';

// =================================
// 기존 타입 (수정 없음)[백엔드의 UserProfile 스키마에 해당]
// =================================
export interface User {
    user_id: string;
    nickname: string;
    email: string;
    role: UserRole
}

//백엔드의 UserProfileResponse 스키마에 해당
export interface UserProfileResponse {
    success: boolean;
    data: {
        user: User;
    };
}


// =================================
// 1. 북마크 관련 타입 (내용 추가)
// =================================

export interface BookmarkItem {
    feed_id: number;
    feed_title: string;
    organization_id: number;
    organization_name: string;
    category_id: number;
    category_name: string;
    view_count: number;
    published_date: string;
    bookmarked_at: string;
}

export interface UserBookmarkListData {
    bookmarks: BookmarkItem[];
    pagination: PaginationInfo;
}

export type UserBookmarkListResponse = DataResponse<UserBookmarkListData>;

// =================================
// 2. 별점 관련 타입 (내용 추가)
// =================================

export interface RatingItem {
    feed_id: number;
    feed_title: string;
    organization_id: number;
    organization_name: string;
    category_id: number;
    category_name: string;
    view_count: number;
    published_date: string;
    user_rating: number;
    average_rating: number;
    rated_at: string;
}

export interface UserRatingListData {
    ratings: RatingItem[];
    pagination: PaginationInfo;
}

export type UserRatingListResponse = DataResponse<UserRatingListData>;