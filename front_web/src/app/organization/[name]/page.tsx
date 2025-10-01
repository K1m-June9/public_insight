"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";

// 1. 필요한 모든 컴포넌트를 임포트합니다.
import OrganizationHeader from "@/components/organization/OrganizationHeader";
import CategoryChart from "@/components/organization/CategoryChart";
import OrganizationWordCloud from "@/components/organization/OrganizationWordCloud";
import LatestPolicyFeeds from "@/components/organization/LatestPolicyFeeds";
import OrganizationTabs from "@/components/organization/OrganizationTabs";
import { ScrollToTopButton } from "@/components/ScrollToTop"

export default function OrganizationPage() {
  const params = useParams();
  const organizationName = decodeURIComponent(params.name as string);

  // 2. 탭과 카테고리 필터링 상태를 페이지 레벨에서 관리
  const [activeTab, setActiveTab] = useState('policy');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);

  const handleCategorySelect = (categoryId: number) => {
    setSelectedCategoryId(prevId => (prevId === categoryId ? null : categoryId));
    // 카테고리 선택 시, 무조건 '정책문서' 탭으로 전환
    setActiveTab('policy');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      {/* 기관 헤더 컴포넌트 */}
      <OrganizationHeader organizationName={organizationName} />

      <main className="flex-grow">
        {/* 3. 새로운 3단 그리드 레이아웃을 적용(좌:1칸, 우:2칸 -> 실제로는 lg:col-span-3으로 3칸) */}
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
            
            {/* Left Sidebar */}
            <div className="lg:col-span-1 space-y-8">
              <CategoryChart
                organizationName={organizationName}
                selectedCategoryId={selectedCategoryId}
                onCategorySelect={handleCategorySelect}
              />
              <OrganizationWordCloud organizationName={organizationName} />
              <LatestPolicyFeeds organizationName={organizationName} />
            </div>
            
            {/* Main Content (Right Area) */}
            <div className="lg:col-span-3">
              <OrganizationTabs
                organizationName={organizationName}
                selectedCategoryId={selectedCategoryId}
                activeTab={activeTab}
                onTabChange={setActiveTab}
              />
            </div>

          </div>
        </div>
      </main>
      <Footer />
      <ScrollToTopButton />
    </div>
  );
}