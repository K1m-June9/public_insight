import { DataResponse, PaginationInfo } from '@/lib/types/base';

// 피드 상태 Enum
export enum FeedStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
}

// 피드 처리 상태 Enum (향후 사용 예정)
export enum ProcessingStatus {
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
}

// 콘텐츠 타입 Enum (백엔드와 동일하게)
export enum ContentType {
  PDF = "pdf",
  TEXT = "text",
}

/**
 * 관리자: 피드 목록의 각 항목에 대한 타입
 */
export interface AdminFeedListItem {
  id: number;
  title: string;
  organization_id: number;
  organization_name: string;
  category_name: string;
  status: FeedStatus;
  // processing_status: ProcessingStatus; // 나중에 추가할 예정
  view_count: number;
  created_at: string;
}

/**
 * 관리자: 피드 목록 데이터 구조
 */
export interface AdminFeedListData {
  feeds: AdminFeedListItem[];
  pagination: PaginationInfo;
}
/**
 * 관리자: 피드 목록 조회 API의 응답 타입
 */
export type AdminFeedListResponse = DataResponse<AdminFeedListData>;

/**
 * 관리자: 피드 목록 조회 API 요청 시 사용할 파라미터 타입
 */
export interface AdminFeedListParams {
  page?: number;
  limit?: number;
  search?: string;
  organization_id?: number;
  category_id?: number;
}

/**
 * 관리자: 기관별 카테고리 항목 타입
 */
export interface AdminOrganizationCategory {
    id: number;
    name: string;
    is_active: boolean;
}
/**
 * 관리자: 기관별 카테고리 조회 API의 응답 타입
 */
export type AdminOrganizationCategoriesResponse = DataResponse<AdminOrganizationCategory[]>;

/**
 * 관리자: 피드 상세 정보 타입
 */
export interface AdminFeedDetail {
  id: number;
  organization_id: number;
  organization_name: string;
  category_id: number;
  category_name: string;
  title: string;
  summary: string | null;
  original_text: string | null;
  source_url: string;
  published_date: string;
  is_active: boolean;
  view_count: number;
  created_at: string;
  updated_at: string;
  content_type: ContentType;
  pdf_url: string | null;
}
/**
 * 관리자: 피드 상세 조회 API의 응답 타입
 */
export type AdminFeedDetailResponse = DataResponse<AdminFeedDetail>;

/**
 * 관리자: 피드 수정 요청 시 Body 타입
 */
export interface AdminFeedUpdateRequest {
  title: string;
  organization_id: number;
  category_id: number;
  summary: string | null;
  original_text: string | null;
  source_url: string;
  is_active: boolean;
}

/**
 * 관리자: 피드 수정 응답 결과 타입
 */
export interface AdminFeedUpdateResult {
  id: number;
  title: string;
  organization_name: string;
  category_name: string;
  updated_at: string;
}
/**
 * 관리자: 피드 수정 API의 응답 타입
 */
export type AdminFeedUpdateResponse = DataResponse<AdminFeedUpdateResult>;