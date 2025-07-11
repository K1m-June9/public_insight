// ============================================================================
// 1. 기본 응답 구조
// ============================================================================

export interface BaseResponse {
    success: boolean;
}

export interface ErrorDetail {
    code: string;
    message: string;
    details?: Record<string, string>;
}

export interface ErrorResponse extends BaseResponse {
    success: false;
    error: ErrorDetail;
}

export interface DataResponse<T> extends BaseResponse {
    success: true;
    data: T;
}

// ============================================================================
// 2. 페이지네이션
// ============================================================================

export interface PaginationInfo {
    current_page: number;
    total_pages: number;
    total_count: number;
    limit: number;
    has_next: boolean;
    has_previous: boolean;
}

export interface PaginatedResponse<T> extends BaseResponse {
    success: true;
    data: T[];
    pagination: PaginationInfo;
}

// ============================================================================
// 3. 공통 열거형 (Enum)
// ============================================================================

export enum SortOrder {
    ASC = "asc",
    DESC = "desc",
}

export enum UserRole {
    USER = "user",
    ADMIN = "admin",
    SUPER_ADMIN = "super_admin",
}

// ============================================================================
// 4. 공통 유틸리티 타입
// ============================================================================

export interface FileInfo {
    filename: string;
    file_url: string;
    file_size?: number;
    content_type?: string;
}

export interface ImageInfo {
    image_url: string;
    alt_text?: string;
    width?: number;
    height?: number;
}

export interface RatingInfo {
    average_rating: number;
    rating_count: number;
}