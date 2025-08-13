"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft, Building } from "lucide-react";
import { useOrganizationSummaryQuery } from "@/hooks/queries/useOrganizationQueries";
import { Button } from "@/components/ui/button";
import { formatNumber } from "@/lib/utils/format";

interface OrganizationHeaderProps {
  organizationName: string;
}

export default function OrganizationHeader({ organizationName }: OrganizationHeaderProps) {
  const router = useRouter();
  const { data: summaryData, isLoading, isError } = useOrganizationSummaryQuery(organizationName);

  const onBack = () => router.back();

  // 로딩 중일 때 스켈레톤 UI 표시
  if (isLoading) {
    return (
      <div className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="h-8 w-24 bg-gray-200 rounded-md mb-6 animate-pulse"></div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
            <div className="lg:col-span-2 space-y-3">
              <div className="h-8 w-1/2 bg-gray-200 rounded-md animate-pulse"></div>
              <div className="h-5 w-3/4 bg-gray-200 rounded-md animate-pulse"></div>
            </div>
            <div className="lg:col-span-1 grid grid-cols-3 gap-4">
              <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
              <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
              <div className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // 에러 발생 시
  if (isError || !summaryData?.success) {
    return (
      <div className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-4 py-6 text-center text-red-500">
            기관 정보를 불러오는 데 실패했습니다.
        </div>
      </div>
    );
  }
  
  const summary = summaryData.data;

  return (
    <div className="border-b border-border bg-card">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center space-x-4 mb-6">
          <Button variant="ghost" size="sm" onClick={onBack} className="flex items-center space-x-2">
            <ArrowLeft className="w-4 h-4" />
            <span>돌아가기</span>
          </Button>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          <div className="lg:col-span-2">
            <div className="flex items-start space-x-4">
              {/* lucide-react 아이콘을 사용합니다. */}
              <div className="bg-accent p-3 rounded-lg">
                <Building className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-foreground">{summary.name}</h1>
                <p className="text-muted-foreground mt-1">{summary.description}</p>
              </div>
            </div>
          </div>
          
          <div className="lg:col-span-1">
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-accent/50 rounded-lg">
                <div className="text-2xl font-bold text-primary mb-1">{formatNumber(summary.stats.documents)}</div>
                <div className="text-xs text-muted-foreground">공개문서</div>
              </div>
              <div className="text-center p-4 bg-accent/50 rounded-lg">
                <div className="text-2xl font-bold text-primary mb-1">{formatNumber(summary.stats.views)}</div>
                <div className="text-xs text-muted-foreground">총 조회수</div>
              </div>
              <div className="text-center p-4 bg-accent/50 rounded-lg">
                <div className="text-2xl font-bold text-primary mb-1">{summary.stats.satisfaction.toFixed(1)}</div>
                <div className="text-xs text-muted-foreground">만족도</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}