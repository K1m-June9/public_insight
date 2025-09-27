"use client";

// 1. 새로운 레이아웃에 맞는 컴포넌트들을 임포트
import { OrganizationList } from "@/components/OrganizationList";
import { TopFeeds } from "@/components/TopFeeds";
import { Notices } from "@/components/Notices";
import { Slider } from "@/components/Slider";
import { FeedList } from "@/components/feed-list";
import { RelatedFeeds } from "@/components/RelatedFeeds"; // "관련 정보" 컴포넌트 추가, 나중에 제대로 만들 예정
import { InsightNavigator } from "@/components/InsightNavigator";

// 2. 필요한 모든 훅을 임포트
import { useOrganizationsForChartQuery } from "@/hooks/queries/useOrganizationQueries";
import { useTop5FeedsQuery } from "@/hooks/queries/useFeedQueries";
import { usePinnedNoticesQuery } from "@/hooks/queries/useNoticeQueries";
import { useSlidersQuery } from "@/hooks/queries/useSliderQueries";

export default function MainContent() {
  // 3. 데이터 페칭 로직은 기존과 동일하게 유지
  //    (PieChart에서 사용하던 latestFeeds는 이제 OrganizationList에서 필요 없으므로 제거 가능)
  const { data: organizationsData, isLoading: isLoadingOrgs } = useOrganizationsForChartQuery();
  const { data: top5FeedsData, isLoading: isLoadingTop5 } = useTop5FeedsQuery(5);
  const { data: pinnedNoticesData, isLoading: isLoadingNotices } = usePinnedNoticesQuery();
  const { data: slidersData, isLoading: isLoadingSliders } = useSlidersQuery();
  
  const isInitialLoading = isLoadingOrgs || isLoadingTop5 || isLoadingNotices || isLoadingSliders;

  // 로딩 스켈레톤 UI
  if (isInitialLoading) {
    return (
        <div className="max-w-7xl mx-auto px-4 py-8">
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Left Sidebar Skeleton */}
                <div className="lg:col-span-1 space-y-8">
                    <div className="h-64 bg-gray-200 rounded-lg animate-pulse"></div>
                    <div className="h-96 bg-gray-200 rounded-lg animate-pulse"></div>
                    <div className="h-64 bg-gray-200 rounded-lg animate-pulse"></div>
                </div>
                {/* Main Content Skeleton */}
                <div className="lg:col-span-2 space-y-8">
                    <div className="h-[450px] bg-gray-200 rounded-lg animate-pulse"></div>
                    <div className="h-[600px] bg-gray-200 rounded-lg animate-pulse"></div>
                </div>
                {/* Right Sidebar Skeleton */}
                <div className="lg:col-span-1 space-y-8">
                    <div className="h-96 bg-gray-200 rounded-lg animate-pulse"></div>
                </div>
            </div>
      </div>
    );
  }

  // 4. 새로운 3단 그리드 레이아웃으로 JSX 구조를 변경
  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Left Sidebar */}
        <div className="lg:col-span-1 space-y-8">
          <OrganizationList chartData={organizationsData?.data} />
          <TopFeeds data={top5FeedsData?.data} />
          <Notices data={pinnedNoticesData?.data} />
        </div>
        
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          <Slider slides={slidersData?.data.sliders} />
          <FeedList />
        </div>
        
        {/* Right Sidebar */}
        <div className="lg:col-span-1 space-y-8">
          <InsightNavigator />
          <RelatedFeeds />
        </div>
        
      </div>
    </div>
  );
}