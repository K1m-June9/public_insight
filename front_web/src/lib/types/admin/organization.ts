import { DataResponse } from '@/lib/types/base';

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
 * 관리자: 카테고리를 포함한 기관 정보 타입
 */
export interface AdminOrganizationWithCategories {
  id: number;
  name: string;
  description: string | null;
  website_url: string | null;
  // icon_path는 제거됨
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