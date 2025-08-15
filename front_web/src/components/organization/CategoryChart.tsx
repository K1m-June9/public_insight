"use client";

import { BarChart3 } from "lucide-react";
import { useOrganizationCategoriesForChartQuery } from "@/hooks/queries/useOrganizationQueries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface CategoryChartProps {
  organizationName: string;
  selectedCategoryId: number | null;
  onCategorySelect: (categoryId: number) => void;
}

export default function CategoryChart({ organizationName, selectedCategoryId, onCategorySelect }: CategoryChartProps) {
  const { data: categoryData, isLoading, isError } = useOrganizationCategoriesForChartQuery(organizationName);

  const categories = categoryData?.data.categories || [];

  if (isLoading) {
    return <div className="bg-gray-200 h-80 rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }
  if (isError) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-destructive" />
            <CardTitle className="text-base font-semibold text-destructive">분야별 문서 현황</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-center text-sm text-muted-foreground py-8">데이터를 불러오는 데 실패했습니다.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          <CardTitle className="text-base font-semibold">분야별 문서 현황</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {categories.map((category) => (
            // 1. 각 항목을 button으로 감싸서 클릭 이벤트 처리
            <button
              key={category.id}
              onClick={() => onCategorySelect(category.id)}
              disabled={category.name === "기타"} // "기타" 항목은 클릭 비활성화
              // 2. cn 유틸리티로 조건부 클래스 적용 (선택됨, 호버 효과)
              className={cn(
                "w-full flex items-center justify-between text-sm p-3 rounded-lg transition-colors text-left",
                category.name !== "기타" && "hover:bg-accent cursor-pointer",
                selectedCategoryId === category.id && "bg-accent"
              )}
            >
              <span className={cn("font-medium", selectedCategoryId === category.id && "text-primary")}>
                {category.name}
              </span>
              <div className="flex items-center space-x-4">
                <span className="text-muted-foreground">{category.percentage}%</span>
                {/* 3. API로 받아온 feed_count 표시 */}
                <span className="text-xs text-muted-foreground w-12 text-right">{category.feed_count}건</span>
              </div>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}