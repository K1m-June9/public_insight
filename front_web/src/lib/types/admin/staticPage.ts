import { DataResponse } from '@/lib/types/base';

/**
 * 관리자: 정적 페이지 목록의 각 항목에 대한 타입
 */
export interface AdminStaticPageListItem {
  id: number;
  slug: string;
  title: string;
  created_at: string;
  updated_at: string;
}
/**
 * 관리자: 정적 페이지 목록 조회 API의 응답 타입
 */
export type AdminStaticPageListResponse = DataResponse<AdminStaticPageListItem[]>;

/**
 * 관리자: 정적 페이지 상세 정보 타입
 */
export interface AdminStaticPageDetail {
  id: number;
  slug: string;
  title: string;
  content: string; // 상세 조회에서는 content 포함(설계하고 약간 달라졌는데 그냥 넘기자)
  created_at: string;
  updated_at: string;
}
/**
 * 관리자: 정적 페이지 상세 조회 API의 응답 타입
 */
export type AdminStaticPageDetailResponse = DataResponse<AdminStaticPageDetail>;

/**
 * 관리자: 정적 페이지 수정 요청 시 Body 타입
 */
export interface AdminStaticPageUpdateRequest {
  content: string;
}
/**
 * 관리자: 정적 페이지 수정 API의 응답 타입
 */
export type AdminStaticPageUpdateResponse = DataResponse<AdminStaticPageDetail>;