// 파일 위치: front_web/src/components/TopFeeds.tsx

"use client";

import { useState } from "react";
import Link from "next/link";
import { Crown, Star, Eye, Bookmark } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Top5FeedData, Top5FeedItem } from "@/lib/types/feed"; // Top5FeedItem 타입 임포트
import { formatNumber } from "@/lib/utils/format"; // 숫자 포맷팅 유틸 임포트
import {Card, CardHeader, CardContent, CardTitle} from "@/components/ui/card"
// 1. Props 타입 정의
interface TopFeedsProps {
  data?: Top5FeedData;
}

// 2. 랭킹 아이템을 위한 별도의 컴포넌트로 분리 (가독성 및 재사용성)
interface RankingItemProps {
  item: Top5FeedItem;
  rank: number;
  activeTab: 'rating' | 'views' | 'bookmarks';
}

function RankingItem({ item, rank, activeTab }: RankingItemProps) {
  const getPrimaryValue = () => {
    switch (activeTab) {
      case 'rating': return item.average_rating.toFixed(1);
      case 'views': return formatNumber(item.view_count);
      case 'bookmarks': return item.bookmark_count;
    }
  };

  const getPrimaryIcon = () => {
    switch (activeTab) {
      case 'rating': return <Star className="w-3 h-3 text-yellow-500 fill-current" />;
      case 'views': return <Eye className="w-3 h-3 text-blue-500" />;
      case 'bookmarks': return <Bookmark className="w-3 h-3 text-green-500" />;
    }
  };
  
  // 순위에 따른 원형 아이콘 스타일
  const rankCircleClass = 
    rank === 1 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white shadow' :
    rank === 2 ? 'bg-gradient-to-br from-gray-300 to-gray-500 text-white shadow' :
    rank === 3 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow' :
    'bg-primary text-primary-foreground';

  return (
    <Link href={`/feed/${item.id}`} className="block">
      <div className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-medium ${rankCircleClass}`}>
            {rank}
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-medium text-foreground truncate">{item.title}</h4>
            <p className="text-xs text-muted-foreground truncate">{item.organization}</p>
          </div>
        </div>
        <div className="flex items-center space-x-1 flex-shrink-0 ml-2">
          {getPrimaryIcon()}
          <span className="text-sm text-muted-foreground w-10 text-left">{getPrimaryValue()}</span>
        </div>
      </div>
    </Link>
  );
}


// 3. 메인 TopFeeds 컴포넌트
export function TopFeeds({ data }: TopFeedsProps) {
  const [activeTab, setActiveTab] = useState<'rating' | 'views' | 'bookmarks'>("rating");

  const topFeedsByRating = data?.top_rated || [];
  const topFeedsByViews = data?.most_viewed || [];
  const topFeedsByBookmarks = data?.most_bookmarked || [];

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center space-x-2">
            <Crown className="w-5 h-5 text-primary" />
            <CardTitle className="text-base font-semibold">TOP 5 리포트</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)} className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-4">
            <TabsTrigger value="rating" className="text-xs flex items-center space-x-1"><Star className="w-3 h-3" /><span>별점</span></TabsTrigger>
            <TabsTrigger value="views" className="text-xs flex items-center space-x-1"><Eye className="w-3 h-3" /><span>조회수</span></TabsTrigger>
            <TabsTrigger value="bookmarks" className="text-xs flex items-center space-x-1"><Bookmark className="w-3 h-3" /><span>북마크</span></TabsTrigger>
          </TabsList>

          <TabsContent value="rating" className="mt-0">
            <div className="space-y-1">
              {topFeedsByRating.map((item, index) => (
                <RankingItem key={item.id} item={item} rank={index + 1} activeTab="rating" />
              ))}
            </div>
          </TabsContent>
          <TabsContent value="views" className="mt-0">
            <div className="space-y-1">
              {topFeedsByViews.map((item, index) => (
                <RankingItem key={item.id} item={item} rank={index + 1} activeTab="views" />
              ))}
            </div>
          </TabsContent>
          <TabsContent value="bookmarks" className="mt-0">
            <div className="space-y-1">
              {topFeedsByBookmarks.map((item, index) => (
                <RankingItem key={item.id} item={item} rank={index + 1} activeTab="bookmarks" />
              ))}
            </div>
          </TabsContent>
        </Tabs>
        
        <div className="mt-4 pt-4 border-t border-border">
          <p className="text-xs text-muted-foreground text-center">
            {activeTab === 'rating' ? '별점 순' : activeTab === 'views' ? '조회수 순' : '북마크 순'} TOP 5
          </p>
        </div>
      </CardContent>
    </Card>
  );
}