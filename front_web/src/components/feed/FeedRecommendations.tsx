"use client";

import Link from "next/link";
import { useFeedRecommendationsQuery } from "@/hooks/queries/useFeedQueries";
import { RecommendedFeedItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";

// UI Components (디자인 시안에서 사용한 컴포넌트들)
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, Newspaper, Calendar } from "lucide-react";

interface FeedRecommendationsProps {
  feedId: number;
  // 현재 피드가 '보도자료'인지 여부를 부모로부터 전달받음
  isSourcePressRelease: boolean; 
}

// 단일 추천 피드 항목을 렌더링하는 내부 컴포넌트 (디자인 시안 기반)
const RecommendedFeedCard = ({ item }: { item: RecommendedFeedItem }) => (
  <Link href={`/feed/${item.id}`} className="block group">
    <div className="cursor-pointer p-4 rounded-lg border border-border hover:bg-muted/50 transition-colors duration-200">
      <div className="space-y-3">
        <div className="flex items-start justify-between gap-3">
          <h4 className="leading-tight text-foreground group-hover:text-primary transition-colors duration-200 line-clamp-2 flex-1 text-sm font-medium">
            {item.title}
          </h4>
          <Badge 
            variant={item.category_name === "보도자료" ? "secondary" : "default"} 
            className="text-xs shrink-0"
          >
            {item.category_name}
          </Badge>
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{item.organization_name}</span>
          {item.published_date && (
            <div className="flex items-center space-x-1">
              <Calendar className="w-3 h-3" />
              <span>{formatDate(item.published_date)}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  </Link>
);

export function FeedRecommendations({ feedId, isSourcePressRelease }: FeedRecommendationsProps) {
  const { data: recoData, isLoading, isError } = useFeedRecommendationsQuery(feedId);

  // 1. API로부터 실제 데이터를 가져옴
  const mainRecommendations = recoData?.data.main_recommendations;
  const subRecommendations = recoData?.data.sub_recommendations;

  // 2. 현재 피드 타입에 따라 탭의 기본값과 각 탭에 표시될 데이터를 결정함
  const defaultTab = isSourcePressRelease ? "press" : "policy";
  const policyTabData = isSourcePressRelease ? subRecommendations : mainRecommendations;
  const pressTabData = isSourcePressRelease ? mainRecommendations : subRecommendations;

  if (isLoading) {
    // 로딩 스켈레톤 UI
    return (
        <div className="space-y-4">
            <h3 className="text-lg font-medium text-foreground">관련 피드</h3>
            <div className="h-10 w-full bg-muted rounded-md animate-pulse"></div>
            <div className="space-y-2 mt-4">
                <div className="h-20 w-full bg-muted rounded-lg animate-pulse"></div>
                <div className="h-20 w-full bg-muted rounded-lg animate-pulse"></div>
            </div>
        </div>
    );
  }
  
  if (isError || (!policyTabData?.length && !pressTabData?.length)) {
    // 에러가 나거나 추천 데이터가 전혀 없으면 컴포넌트 자체를 렌더링하지 않음
    return null;
  }
  
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium text-foreground">관련 피드</h3>
      
      <Tabs defaultValue={defaultTab} className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="policy" className="flex items-center space-x-2" disabled={!policyTabData?.length}>
            <FileText className="w-4 h-4" />
            <span>정책자료</span>
          </TabsTrigger>
          <TabsTrigger value="press" className="flex items-center space-x-2" disabled={!pressTabData?.length}>
            <Newspaper className="w-4 h-4" />
            <span>보도자료</span>
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="policy" className="space-y-2 mt-4">
          {policyTabData?.map(item => <RecommendedFeedCard key={item.id} item={item} />)}
        </TabsContent>
        
        <TabsContent value="press" className="space-y-2 mt-4">
          {pressTabData?.map(item => <RecommendedFeedCard key={item.id} item={item} />)}
        </TabsContent>
      </Tabs>
    </div>
  );
}