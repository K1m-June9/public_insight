import { DataResponse } from './base';

// =================================
// 1. 정적 페이지 관련
// =================================

export interface StaticPageContent {
    slug: string;
    content: string; // Markdown에서 변환된 HTML 문자열
}

export interface StaticPageData {
    page: StaticPageContent;
}

export type StaticPageResponse = DataResponse<StaticPageData>;

// =================================
// 2. 지원되는 Slug 열거형
// =================================

export enum SupportedSlug {
    ABOUT = "about",
    TERMS = "terms",
    PRIVACY = "privacy",
    YOUTH_PROTECTION = "youth-protection",
    INVALID_PAGE = "invalid-page",
}