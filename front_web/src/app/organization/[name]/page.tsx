"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Header from "@/components/header";
import Footer from "@/components/footer";
import OrganizationPieChart from "@/components/organization/organization-pie-chart";
import OrganizationWordCloud from "@/components/organization/organization-word-cloud";
import OrganizationCommunity from "@/components/organization/organization-community";
import OrganizationPress from "@/components/organization/organization-press";
import OrganizationFeedList from "@/components/organization/organization-feed-list";

export default function OrganizationPage() {
  const params = useParams();
  const organizationName = params.name as string;
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | null>(null);

  const handleCategorySelect = (categoryId: number) => {
    setSelectedCategoryId(prevId => (prevId === categoryId ? null : categoryId));
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="w-full px-4 py-8 md:px-6">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* 좌측 컨텐츠 (45%) */}
            <div className="w-full lg:w-[45%]">
              <div className="space-y-8">
                <OrganizationPieChart
                  organizationName={organizationName}
                  selectedCategoryId={selectedCategoryId}
                  onCategorySelect={handleCategorySelect}
                />
                <OrganizationWordCloud organizationName={organizationName} />
                <OrganizationCommunity organizationName={organizationName} />
                <OrganizationPress organizationName={organizationName} />
              </div>
            </div>

            {/* 우측 컨텐츠 (55%) */}
            <div className="w-full lg:w-[55%]">
              <OrganizationFeedList
                organizationName={organizationName}
                selectedCategoryId={selectedCategoryId}
              />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}