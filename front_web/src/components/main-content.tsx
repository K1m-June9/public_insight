"use client";

import { PieChart } from "@/components/pie-chart";
import { TopFeeds } from "@/components/top-feeds";
import { Notices } from "@/components/notices";
import { Slider } from "@/components/slider";
import { FeedList } from "@/components/feed-list";

// Queries
import { useOrganizationsForChartQuery } from "@/hooks/queries/useOrganizationQueries";
import { useLatestFeedsQuery, useTop5FeedsQuery } from "@/hooks/queries/useFeedQueries";
import { usePinnedNoticesQuery } from "@/hooks/queries/useNoticeQueries";
import { useSlidersQuery } from "@/hooks/queries/useSliderQueries";

export default function MainContent() {
  // 1. 메인 페이지에 필요한 모든 데이터를 병렬로 불러옴
  const { data: organizationsData, isLoading: isLoadingOrgs } = useOrganizationsForChartQuery();
  const { data: latestFeedsData, isLoading: isLoadingLatestFeeds } = useLatestFeedsQuery(6); // PieChart에서 6개 사용
  const { data: top5FeedsData, isLoading: isLoadingTop5 } = useTop5FeedsQuery(5);
  const { data: pinnedNoticesData, isLoading: isLoadingNotices } = usePinnedNoticesQuery();
  const { data: slidersData, isLoading: isLoadingSliders } = useSlidersQuery();
  
  // 전체 로딩 상태를 확인
  const isInitialLoading = 
    isLoadingOrgs || isLoadingLatestFeeds || isLoadingTop5 || isLoadingNotices || isLoadingSliders;

  // 로딩 중일 때 보여줄 스켈레톤 UI (선택사항)
  if (isInitialLoading) {
    return (
      <div className="w-full px-4 py-8 md:px-6">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* 좌측 스켈레톤 */}
          <div className="w-full lg:w-[45%] space-y-8">
            <div className="h-[500px] bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="h-[300px] bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="h-[200px] bg-gray-200 rounded-lg animate-pulse"></div>
          </div>
          {/* 우측 스켈레톤 */}
          <div className="w-full lg:w-[55%] space-y-8">
            <div className="h-[350px] bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="h-[600px] bg-gray-200 rounded-lg animate-pulse"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full px-4 py-8 md:px-6">
      <div className="flex flex-col lg:flex-row gap-8">
        {/* 좌측 컨텐츠 (45%) */}
        {/*<div className="w-full lg:w-[45%]">*/}
        <div className="w-full lg:w-[45%] overflow-y-auto" style={{ maxHeight: "calc(100vh - 16rem)" }}>
          <div className="space-y-8">
            {/* 2. 각 컴포넌트에 필요한 데이터를 props로 전달 */}
            <PieChart 
              chartData={organizationsData?.data} 
              latestFeeds={latestFeedsData?.data} 
            />
            <TopFeeds data={top5FeedsData?.data} />
            <Notices data={pinnedNoticesData?.data} />
          </div>
        </div>

        {/* 우측 컨텐츠 (55%) */}
        {/*<div className="w-full lg:w-[55%]">*/}
        <div className="w-full lg:w-[55%] overflow-y-auto" style={{ maxHeight: "calc(100vh - 16rem)" }}>
          <div>
            <Slider slides={slidersData?.data.sliders} />
            <FeedList /> {/* FeedList는 자체적으로 페이지네이션을 관리하므로 props가 필요 없을 수 있음 */}
          </div>
        </div>
      </div>
    </div>
  );
}