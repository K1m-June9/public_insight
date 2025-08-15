"use client";

import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { MainFeedItem } from "@/lib/types/feed"; // 가상 데이터 타입을 위해 임포트
import { formatDate } from "@/lib/utils/date";

// 1. 나중에 API로 대체될 Mock 데이터 생성
const mockFeeds: Omit<MainFeedItem, 'view_count' | 'average_rating' | 'bookmark_count'>[] = [
  {
    id: 9001,
    title: "준비중입니다.",
    summary: "준비중입니다.",
    organization: { id: 999, name: "미정" },
    published_date: "2025-07-19T00:00:00Z",
  }
];

export function RelatedFeeds() {
  return (
    <section>
      <h3 className="mb-6 text-lg font-semibold text-primary">관련 정보</h3>
      <div className="space-y-4">
        {mockFeeds.map((feed) => (
          <Link href={`/feed/${feed.id}`} key={feed.id} className="block">
            <div className="bg-card border border-border rounded-lg p-4 hover:shadow-md transition-all">
              <Badge variant="secondary" className="text-xs mb-2">
                {feed.organization.name}
              </Badge>
              <h4 className="mb-2 leading-tight font-medium hover:text-primary transition-colors">
                {feed.title}
              </h4>
              <p className="text-sm text-muted-foreground mb-3 leading-relaxed line-clamp-2">
                {feed.summary}
              </p>
              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <span>{formatDate(feed.published_date)}</span>
              </div>
            </div>
          </Link>
        ))}
      </div>
      
      <div className="text-center mt-6">
        <Button 
          variant="outline" 
          size="sm" 
          className="w-full"
          // 현재는 기능이 없으므로, 클릭 시 전체 피드 목록으로 이동하도록 설정
          asChild
        >
          <Link href="/feeds">더 많은 소식 보기</Link> 
        </Button>
      </div>
    </section>
  );
}