"use client";

import { useAdminDashboardQuery } from "@/hooks/queries/useAdminDashboardQueries";

// Child Components
import { DashboardOverview } from "@/components/admin/dashboard/DashboardOverview";
import { MonthlySignupsChart } from "@/components/admin/dashboard/MonthlySignupsChart";
import { PopularKeywords } from "@/components/admin/dashboard/PopularKeywords";
import { ContentStats } from "@/components/admin/dashboard/ContentStats";
import { TopFeeds } from "@/components/admin/dashboard/TopFeeds";
import { RecentActivities } from "@/components/admin/dashboard/RecentActivities";

export default function DashboardClient() {
  const { data: dashboardResponse, isLoading, isError } = useAdminDashboardQuery();
  const data = dashboardResponse?.data;

  if (isLoading) {
    return <div className="text-center p-10">대시보드 데이터를 불러오는 중...</div>;
  }

  if (isError || !data) {
    return <div className="text-center p-10 text-destructive">데이터를 불러오는 데 실패했습니다.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold tracking-tight">대시보드</h2>

      {/* 1. 개요 통계 */}
      <DashboardOverview stats={data} />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* 2. 월별 가입자 수 차트 */}
        <div className="lg:col-span-2">
          <MonthlySignupsChart data={data.monthly_signups} />
        </div>
        
        {/* 3. 콘텐츠 및 키워드 통계 */}
        <div className="space-y-6">
          <ContentStats notices={data.notice_stats} sliders={data.slider_stats} orgs={data.organization_stats} />
          <PopularKeywords keywords={data.popular_keywords} />
        </div>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* 4. 인기 피드 목록 */}
        <TopFeeds title="인기 북마크 피드" type="bookmark" data={data.top_bookmarked_feeds} />
        <TopFeeds title="인기 평점 피드" type="rating" data={data.top_rated_feeds} />
        
        {/* 5. 최근 활동 로그 */}
        <RecentActivities activities={data.recent_activities} />
      </div>
    </div>
  );
}