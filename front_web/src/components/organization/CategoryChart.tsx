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
    // --- 💡 수정된 부분 1: Card의 기본 패딩을 p-6으로 늘립니다. ---
    <Card className="shadow-sm hover:shadow-md transition-shadow p-6">
      {/* --- 💡 수정된 부분 2: CardHeader의 패딩을 없애고 제목 아래 마진을 추가합니다. --- */}
      <CardHeader className="p-0 mb-0">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          {/* --- 💡 수정된 부분 3: CardTitle의 스타일을 다른 컴포넌트와 통일합니다. --- */}
          <CardTitle className="text-primary text-lg font-medium">분야별 문서 현황</CardTitle>
        </div>
      </CardHeader>
      {/* --- 💡 수정된 부분 4: CardContent의 패딩을 제거하여 이중 여백을 방지합니다. --- */}
      <CardContent className="p-0">
        <div className="space-y-3">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => onCategorySelect(category.id)}
              disabled={category.name === "기타"}
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
                <span className="text-muted-foreground">{Number(category.percentage).toFixed(1)}%</span>
                {/* --- 💡 수정된 부분 5: 고정 너비(w-12)를 제거하여 자연스러운 정렬을 유도합니다. --- */}
                <span className="text-xs text-muted-foreground text-right">{category.feed_count}건</span>
              </div>
            </button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}