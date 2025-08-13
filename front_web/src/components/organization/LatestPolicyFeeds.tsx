"use client";

import Link from "next/link";
import { FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useOrganizationLatestFeedsQuery } from "@/hooks/queries/useFeedQueries";

interface LatestPolicyFeedsProps {
  organizationName: string;
}

export default function LatestPolicyFeeds({ organizationName }: LatestPolicyFeedsProps) {
  // 1. 기존에 만들어 둔 훅을 사용하여 최신 피드 5개를 가져옴
  const { data: latestFeedsData, isLoading, isError } = useOrganizationLatestFeedsQuery(organizationName, 5);

  const feeds = latestFeedsData?.data.feeds || [];

  if (isLoading) {
    return <div className="bg-gray-200 h-72 rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  if (isError) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <FileText className="w-5 h-5 text-destructive" />
            <CardTitle className="text-base font-semibold text-destructive">최신 정책자료</CardTitle>
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
          <FileText className="w-5 h-5 text-primary" />
          <CardTitle className="text-base font-semibold">최신 정책자료</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {feeds.length > 0 ? (
            feeds.map((feed) => (
              // 2. 각 아이템을 Link 컴포넌트로 감싸서 클릭 시 이동하도록 구현
              <Link
                href={`/feed/${feed.id}`}
                key={feed.id}
                className="block p-3 rounded-md border border-border/50 hover:border-primary/50 transition-colors cursor-pointer hover:bg-accent/50"
              >
                <div className="flex flex-col space-y-2">
                  <h4 className="text-sm font-medium leading-relaxed line-clamp-2">
                    {feed.title}
                  </h4>
                  <Badge variant="secondary" className="self-start text-xs">
                    {feed.category.name}
                  </Badge>
                </div>
              </Link>
            ))
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">최신 정책자료가 없습니다.</p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}