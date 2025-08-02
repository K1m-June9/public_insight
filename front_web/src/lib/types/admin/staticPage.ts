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