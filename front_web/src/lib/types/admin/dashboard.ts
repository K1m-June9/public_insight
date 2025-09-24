import { DataResponse } from '@/lib/types/base';
import { ActivityType } from '@/lib/types/admin/user'; // user 타입에서 재사용

/** 기본 통계 타입 */
export interface AdminDailySignupStat {
  date: string; // date 타입은 string으로 받습니다.
  count: number;
}

export interface AdminPopularKeyword {
  keyword: string;
  count: number;
}

export interface AdminOrganizationStat {
  organization_name: string;
  feed_count: number;
}

/** 콘텐츠 통계 타입 */
export interface AdminSliderStats {
  active: number;
  inactive: number;
}

export interface AdminNoticeStats {
  active: number;
  inactive: number;
  pinned: number;
}

/** 인기 피드 타입 */
export interface AdminTopBookmarkedFeed {
  id: number;
  title: string;
  bookmark_count: number;
  organization_name: string;
}

export interface AdminTopRatedFeed {
  id: number;
  title: string;
  average_rating: number;
  rating_count: number;
  organization_name: string;
}

/** 최근 활동 타입 */
export interface AdminRecentActivity {
  id: number;
  activity_type: ActivityType;
  user_name: string;
  target_id: number | null;
  created_at: string;
}

/** 대시보드 전체 데이터 구조 */
export interface AdminDashboardData {
  // 개요 통계
  total_users: number;
  active_users: number;
  total_feeds: number;
  total_organizations: number;
  today_signups: number;
  total_views: number;
  
  // 시계열 데이터
  monthly_signups: AdminDailySignupStat[];
  
  // 검색 통계
  popular_keywords: AdminPopularKeyword[];
  
  // 기관 통계
  organization_stats: AdminOrganizationStat[];
  
  // 콘텐츠 통계
  slider_stats: AdminSliderStats;
  notice_stats: AdminNoticeStats;
  
  // 인기 피드
  top_bookmarked_feeds: AdminTopBookmarkedFeed[];
  top_rated_feeds: AdminTopRatedFeed[];
  
  // 최근 활동
  recent_activities: AdminRecentActivity[];
}

/** 대시보드 API 응답 타입 */
export type AdminDashboardResponse = DataResponse<AdminDashboardData>;