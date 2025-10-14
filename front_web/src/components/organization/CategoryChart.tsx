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
  const categoriesToRender = categoryData?.data.categories.filter((category) => category.feed_count > 0) || [];
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
            <CardTitle className="text-base font-semibold text-destructive">분야별 정책 문서 현황</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-center text-sm text-muted-foreground py-8">데이터를 불러오는 데 실패했습니다.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow p-6">
      <CardHeader className="p-0 mb-0">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">분야별 정책 문서 현황</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="space-y-3">
          {/* --- ▼ [수정] 원본 categories 배열 대신, 필터링된 categoriesToRender 배열을 사용합니다. ▼ --- */}
          {categoriesToRender.map((category) => (
            <button
              key={category.id}
              onClick={() => onCategorySelect(category.id)}
              // 이제 '기타' 항목이 없으므로 disabled 로직은 제거해도 되지만, 안전을 위해 유지합니다.
              disabled={category.name === "기타"}
              className={cn(
                "w-full flex items-center justify-between text-sm p-3 rounded-lg transition-colors text-left",
                "hover:bg-accent cursor-pointer", // '기타'가 없으므로 항상 hover 효과 적용
                selectedCategoryId === category.id && "bg-accent"
              )}
            >
              <span className={cn("font-medium", selectedCategoryId === category.id && "text-primary")}>
                {category.name}
              </span>
              <div className="flex items-center space-x-4">
                <span className="text-xs text-muted-foreground text-right">{category.feed_count}건</span>
              </div>
            </button>
          ))}
        </div>
        <div className="mt-6 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            선택 시 해당 카테고리의<br />
          정책 문서만 제공됩니다.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}