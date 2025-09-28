"use client";

import Link from "next/link";
// 🔧 1. '탐색'의 의미를 담은 Compass 아이콘을 사용
import { Compass } from "lucide-react";
// 🔧 2. 우리가 새로 만든 useWordCloudQuery 훅을 임포트
import { useWordCloudQuery } from "@/hooks/queries/useGraphQueries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { WordCloudItem } from "@/lib/types/graph"; // 🔧 3. 키워드 아이템 타입을 임포트

// 4. 아이템 렌더링을 위한 별도의 컴포넌트로 분리 (TopFeeds 패턴과 동일)
interface TopicGuideItemProps {
  item: WordCloudItem;
  rank: number;
}

function TopicGuideItem({ item, rank }: TopicGuideItemProps) {
  // 순위에 따른 원형 아이콘 스타일
  const rankCircleClass =
    rank === 1 ? "bg-gradient-to-br from-blue-500 to-blue-700 text-white shadow" :
    rank === 2 ? "bg-gradient-to-br from-sky-400 to-sky-600 text-white shadow" :
    rank === 3 ? "bg-gradient-to-br from-cyan-400 to-cyan-600 text-white shadow" :
    "bg-muted text-muted-foreground";

  return (
    // 5. 각 아이템을 클릭하면 /explore 페이지로 이동하는 링크
    <Link href={`/explore?keyword=${encodeURIComponent(item.text)}`} className="block group">
      <div className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ${rankCircleClass}`}>
            {rank}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-foreground truncate group-hover:text-primary transition-colors">
              {item.text}
            </h4>
          </div>
        </div>
        {/* 
          💡 value(인기 점수)를 시각적으로 보여주고 싶다면 여기에 추가 가능
            예: <div className="text-xs text-muted-foreground">{item.value.toFixed(1)}</div>
        */}
      </div>
    </Link>
  );
}

// 6. 메인 InsightNavigator 컴포넌트
export function InsightNavigator() {
  // 7. useWordCloudQuery 훅을 호출하여 '전체' 인기 키워드 상위 10개를 가져옴
  //    organizationName을 전달하지 않으면 메인 페이지용 데이터를 가져옴
  const { data: response, isLoading, isError } = useWordCloudQuery({
    limit: 10,
  });

  const keywords = response?.data || [];

  // 로딩 상태 UI
  if (isLoading) {
    // TopFeeds와 유사한 높이의 스켈레톤
    return <div className="h-[480px] bg-gray-200 rounded-lg animate-pulse"></div>;
  }

  // 에러 상태 UI
  if (isError) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Compass className="w-5 h-5 text-destructive" />
            <CardTitle className="text-base font-semibold text-destructive">토픽 가이드</CardTitle>
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
          <Compass className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">토픽 가이드</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        {keywords.length > 0 ? (
          <div className="space-y-1">
            {keywords.map((item, index) => (
              <TopicGuideItem key={item.text} item={item} rank={index + 1} />
            ))}
          </div>
        ) : (
          <div className="text-center text-sm text-muted-foreground py-8">
            <p>현재 인기있는 토픽이 없습니다.</p>
          </div>
        )}
        <div className="mt-6 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            키워드 선택 시<br />
          마인드맵 페이지로 이동합니다
          </p>
        </div>
      </CardContent>
    </Card>
  );
}