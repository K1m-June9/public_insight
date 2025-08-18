"use client";

import { Cloud } from "lucide-react";
import { useOrganizationWordCloudQuery } from "@/hooks/queries/useOrganizationQueries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface OrganizationWordCloudProps {
  organizationName: string;
}

export default function OrganizationWordCloud({ organizationName }: OrganizationWordCloudProps) {
  const { data: wordCloudData, isLoading, isError } = useOrganizationWordCloudQuery(organizationName);

  // 1. API 응답에서 키워드 목록을 가져옵니다.
  const keywords = wordCloudData?.data.keywords || [];

  // 로딩 상태 UI
  if (isLoading) {
    return <div className="bg-gray-200 h-[300px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  // 에러 상태 UI
  if (isError) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Cloud className="w-5 h-5 text-destructive" />
            <CardTitle className="text-base font-semibold text-destructive">주요 키워드</CardTitle>
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
          <Cloud className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">주요 키워드</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {keywords.length > 0 ? (
          <div className="relative h-64 flex flex-wrap items-center justify-center gap-2 overflow-hidden">
            {keywords.map((word) => (
              <span
                key={word.text}
                className="inline-block transition-all duration-300 hover:scale-110 cursor-pointer"
                style={{
                  fontSize: `${word.size}px`,
                  color: word.color,
                  fontWeight: word.weight,
                }}
              >
                {word.text}
              </span>
            ))}
          </div>
        ) : (
          <div className="relative h-64 flex items-center justify-center">
            <p className="text-muted-foreground">표시할 주요 키워드가 없습니다.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}