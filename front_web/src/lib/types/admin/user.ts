import { BaseResponse, DataResponse, PaginationInfo } from '@/lib/types/base';

// 열거형 (Enum)
export enum UserRole {
  USER = "user",
  MODERATOR = "moderator",
  ADMIN = "admin",
}

export enum UserStatus {
  ACTIVE = "active",
  INACTIVE = "inactive",
  SUSPENDED = "suspended",
  DELETED = "deleted",
}

export enum ActivityType {
  LOGIN = "LOGIN",
  LOGOUT = "LOGOUT",
  FEED_VIEW = "FEED_VIEW",
  FEED_BOOKMARK = "FEED_BOOKMARK",
  FEED_RATING = "FEED_RATING",
  SEARCH = "SEARCH",
  PROFILE_UPDATE = "PROFILE_UPDATE",
}

// 사용자 목록 관련 타입
export interface AdminUserListItem {
  id: number;
  user_id: string;
  nickname: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  created_at: string;
}

export interface AdminUserRoleStats {
  admin: number;
  moderator: number;
  user: number;
}

export interface AdminUserStatusStats {
  active: number;
  inactive: number;
  suspended: number;
  deleted: number;
}

export interface AdminUserListStatistics {
  total_users: number;
  by_role: AdminUserRoleStats;
  by_status: AdminUserStatusStats;
}

export interface AdminUserListData {
  users: AdminUserListItem[];
  pagination: PaginationInfo;
  statistics: AdminUserListStatistics;
}

export type AdminUserListResponse = DataResponse<AdminUserListData>;

// 사용자 상세 관련 타입
export interface AdminUserStatistics {
  total_bookmarks: number;
  total_ratings: number;
  total_searches: number;
  total_activities: number;
  last_activity_at: string | null;
}

export interface AdminUserDetail {
  id: number;
  user_id: string;
  email: string;
  nickname: string;
  role: UserRole;
  status: UserStatus;
  terms_agreed: boolean;
  privacy_agreed: boolean;
  notification_agreed: boolean;
  created_at: string;
  updated_at: string;
  statistics: AdminUserStatistics;
}

export type AdminUserDetailResponse = DataResponse<AdminUserDetail>;

// 사용자 활동 로그 관련 타입
export interface AdminUserActivity {
  id: string; // Elasticsearch _id는 문자열
  activity_type: ActivityType;
  target_id: number | null;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export interface AdminUserActivityData {
  activities: AdminUserActivity[];
  pagination: PaginationInfo;
}

export type AdminUserActivityResponse = DataResponse<AdminUserActivityData>;

// 요청 Body 및 파라미터 타입
export interface AdminUserListRequestParams {
  page?: number;
  limit?: number;
  search?: string;
  role?: UserRole;
  status?: UserStatus;
}

export interface AdminUserRoleChangeRequest {
  role: UserRole;
}

export interface AdminUserStatusChangeRequest {
  status: UserStatus;
}

// 응답 타입 (상태/역할 변경)
export interface AdminUserRoleUpdate {
    id: number;
    user_id: string;
    nickname: string;
    role: UserRole;
    updated_at: string;
}
export type AdminUserRoleChangeResponse = DataResponse<AdminUserRoleUpdate>;

export interface AdminUserStatusUpdate {
    id: number;
    user_id: string;
    nickname: string;
    status: UserStatus;
    updated_at: string;
}
export type AdminUserStatusChangeResponse = DataResponse<AdminUserStatusUpdate>;