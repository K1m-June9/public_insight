import { BaseResponse, DataResponse } from '@/lib/types/base';

/**
 * 관리자 필터링용 기관 정보 (ID와 이름만 포함)
 */
export interface AdminSimpleOrganizationItem {
  id: number;
  name: string;
}

/**
 * 관리자 필터링용 기관 목록 조회 API의 응답 타입
 */
export type AdminSimpleOrganizationListResponse = DataResponse<AdminSimpleOrganizationItem[]>;

/**
 * 관리자: 기관에 속한 카테고리 항목 타입
 */
export interface AdminCategoryItem {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  feed_count: number;
  created_at: string;
  updated_at: string | null;
}

/**
 * 관리자: 카테고리를 포함한 기관 정보 타입 (목록용)
 */
export interface AdminOrganizationWithCategories {
  id: number;
  name: string;
  description: string | null;
  website_url: string | null;
  // iconUrl은 제거됨
  is_active: boolean;
  feed_count: number;
  created_at: string;
  updated_at: string | null;
  categories: AdminCategoryItem[];
}

/**
 * 관리자: 기관 목록 조회 API의 응답 타입
 */
export type AdminOrganizationListResponse = DataResponse<AdminOrganizationWithCategories[]>;


/**
 * 관리자: 기관 상세 정보 타입
 */
export interface AdminOrganizationDetail {
    id: number;
    name: string;
    description: string;
    website_url: string | null;
    is_active: boolean;
    feed_count: number;
    created_at: string;
    updated_at: string | null;
}

/**
 * 관리자: 기관 상세 조회 API 응답 타입
 */
export type AdminOrganizationDetailResponse = DataResponse<AdminOrganizationDetail>;


/**
 * 관리자: 카테고리 상세 정보 타입
 */
export interface AdminCategoryDetail {
  id: number;
  organization_id: number;
  organization_name: string;
  name: string;
  description: string | null;
  is_active: boolean;
  feed_count: number;
  created_at: string;
  updated_at: string | null;
}

/**
 * 관리자: 카테고리 상세 조회 API 응답 타입
 */
export type AdminCategoryDetailResponse = DataResponse<AdminCategoryDetail>;

/** 관리자: 카테고리 생성 응답 타입 */
export type AdminCategoryCreateResponse = DataResponse<AdminCategoryDetail>;

/** 관리자: 카테고리 수정 응답 타입 */
export type AdminCategoryUpdateResponse = DataResponse<AdminCategoryDetail>;


/** 관리자: 기관 생성/수정 시 Body 타입 */
export interface AdminOrganizationRequest {
  name: string;
  description: string | null;
  website_url: string | null;
  is_active: boolean;
}

/** 관리자: 카테고리 생성 요청 시 Body 타입 */
export interface AdminCategoryCreateRequest {
  organization_id: number;
  name: string;
  description: string | null;
  is_active: boolean;
}

/** 관리자: 카테고리 수정 요청 시 Body 타입 */
export interface AdminCategoryUpdateRequest {
  organization_id: number;
  name: string;
  description: string | null;
  is_active: boolean;
}

// 생성 응답 타입 (카테고리 포함)
export type AdminOrganizationCreateResponse = DataResponse<AdminOrganizationWithCategories>;

// 수정 응답 타입 (카테고리 미포함)
export type AdminOrganizationUpdateResponse = DataResponse<AdminOrganizationDetail>;
/** 관리자: 기관/카테고리 삭제 응답 타입 */
export type AdminDeleteResponse = BaseResponse;