"use client";

import Link from "next/link";
import { TrendingUp, Heart, Eye, Bookmark, Star } from "lucide-react";
import { useUserRecommendationsQuery } from "@/hooks/queries/useUserQueries";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/date";

export default function RecommendationTab() {
  const { data: recoData, isLoading, isError } = useUserRecommendationsQuery();

  if (isLoading) {
    return <div className="text-center py-8">맞춤 추천 정보를 불러오는 중...</div>;
  }
  if (isError) {
    return <div className="text-center py-8 text-red-500">추천 정보를 불러오는 중 오류가 발생했습니다.</div>;
  }

  const recommendations = recoData?.data;
  const keywords = recommendations?.recommended_keywords || [];
  const feeds = recommendations?.recommended_feeds || [];

  return (
    <div className="space-y-12">
      {/* 1. 키워드 트렌드 섹션 */}
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-primary" />
          회원님을 위한 추천 키워드
        </h2>
        {keywords.length > 0 ? (
          <div className="grid gap-4 md:grid-cols-2">
            {keywords.map((item) => (
              <Link href={`/explore?keyword=${encodeURIComponent(item.keyword)}`} key={item.keyword}>
                <Card className="p-4 hover:bg-muted/50 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-foreground">{item.keyword}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-muted rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary rounded-full"
                          // score가 0~1 사이 값이므로, 100을 곱해 퍼센트로 변환
                          style={{ width: `${(item.score ?? 0) * 100}%` }} 
                        />
                      </div>
                      <span className="text-xs text-muted-foreground min-w-[32px] text-right">
                        {Math.round((item.score ?? 0) * 100)}
                      </span>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">추천 키워드가 없습니다.</div>
        )}
      </div>

      {/* 2. 맞춤 추천 피드 섹션 */}
      <div>
        <h2 className="text-xl font-semibold text-foreground mb-4 flex items-center gap-2">
          <Heart className="w-5 h-5 text-primary" />
          회원님을 위한 맞춤 피드
          {recommendations?.is_personalized === false && (
            <Badge variant="outline" className="text-xs">인기 피드</Badge>
          )}
        </h2>
        {feeds.length > 0 ? (
          <div className="grid gap-6">
            {feeds.map((feed) => (
              <Link href={`/feed/${feed.id}`} key={feed.id}>
                <Card className="p-6 hover:shadow-md transition-shadow cursor-pointer">
                  <div className="space-y-3">
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary">{feed.organization_name}</Badge>
                      <Badge variant="outline">{feed.category_name}</Badge>
                    </div>
                    <h3 className="font-semibold text-lg text-foreground leading-tight hover:text-primary transition-colors">
                      {feed.title}
                    </h3>
                    {feed.summary && (
                      <p className="text-sm text-muted-foreground leading-relaxed line-clamp-2">
                        {feed.summary}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between pt-3 border-t text-sm text-muted-foreground">
                      {feed.published_date ? (
                        <span>{formatDate(feed.published_date)}</span>
                      ) : (
                        <span></span> 
                      )}
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center gap-1">
                          <Eye className="h-4 w-4" />
                          <span>{feed.view_count.toLocaleString()}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Star className="h-4 w-4 text-yellow-400 fill-current" />
                          <span>{feed.average_rating.toFixed(1)}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Bookmark className="h-4 w-4" />
                          <span>{feed.bookmark_count.toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">추천 피드가 없습니다.</div>
        )}
      </div>
    </div>
  );
}