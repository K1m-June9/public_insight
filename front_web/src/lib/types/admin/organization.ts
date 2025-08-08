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