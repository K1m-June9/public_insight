import { BaseResponse, DataResponse } from '@/lib/types/base';

/**
 * 관리자: 슬라이더 목록의 각 항목에 대한 타입
 */
export interface AdminSliderListItem {
  id: number;
  title: string;
  tag: string;
  image_path: string; // 백엔드에서는 image_path로 URL을 전달
  display_order: number;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
}

/**
 * 관리자: 슬라이더 상세 정보 타입
 */
export interface AdminSliderDetail {
  id: number;
  title: string;
  preview: string;
  tag: string;
  content: string;
  author: string;
  image_url: string; // 스키마의 'image' 필드를 컨벤션에 맞게 url로 명명
  display_order: number;
  is_active: boolean;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string | null;
}

/** 관리자: 슬라이더 생성/수정 요청 시 form 필드 타입 (파일 제외) */
export interface AdminSliderFormRequest {
  title: string;
  preview: string;
  tag: string;
  content: string;
  display_order: number;
  start_date: string | null;
  end_date: string | null;
}

/** 관리자: 슬라이더 상태 수정 요청 Body 타입 */
export interface AdminSliderStatusUpdateRequest {
  is_active: boolean;
}

/** 관리자: 슬라이더 목록 조회 API 응답 타입 */
export type AdminSliderListResponse = DataResponse<AdminSliderListItem[]>;
/** 관리자: 슬라이더 상세/생성/수정 API 응답 타입 */
export type AdminSliderResponse = DataResponse<AdminSliderDetail>;
/** 관리자: 슬라이더 상태 수정 API 응답 타입 */
export type AdminSliderStatusUpdateResponse = BaseResponse & { data: { id: number; is_active: boolean; updated_at: string }};
/** 관리자: 슬라이더 삭제 API 응답 타입 */
export type AdminSliderDeleteResponse = BaseResponse & { message: string };