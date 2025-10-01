"use client";

import Link from "next/link"; 
import { useRelatedKeywordsQuery } from "@/hooks/queries/useGraphQueries"; 
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Sparkles } from "lucide-react";

interface KeywordSectionProps {
  feedId: number; 
}

export default function KeywordSection({ feedId }: KeywordSectionProps) {
  
  const { data: response, isLoading, isError } = useRelatedKeywordsQuery(feedId, {
    enabled: !!feedId && feedId > 0,
    limit: 7,
  });

  const keywords = response?.data || [];

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Sparkles className="w-5 h-5 text-primary" />
            관련 토픽
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 animate-pulse">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-12 bg-muted rounded-lg" />
          ))}
        </CardContent>
      </Card>
    );
  }

  if (isError) {
    return null;
  }
  
  if (keywords.length === 0) {
      return (
          <Card>
              <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-base">
                      <Sparkles className="w-5 h-5 text-primary" />
                      주요 키워드
                  </CardTitle>
              </CardHeader>
              <CardContent>
                  <p className="text-sm text-muted-foreground text-center py-8">
                      관련된 내용을 찾을 수 없습니다.
                  </p>
              </CardContent>
          </Card>
      )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="w-5 h-5 text-primary" />
          주요 키워드
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {keywords.map((item, index) => (
            <Link 
              key={item.text} 
              href={`/explore?keyword=${encodeURIComponent(item.text)}`}
              className="block"
            >
              <div
                className="flex items-center justify-between p-3 bg-card rounded-lg hover:bg-muted/50 transition-colors cursor-pointer group border"
              >
                <div className="flex items-center gap-3">
                  <Badge variant="secondary" className="text-xs px-2 py-1">
                    {index + 1}
                  </Badge>
                  <span className="text-sm font-medium group-hover:text-primary transition-colors">
                    {item.text}
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-12 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-primary rounded-full transition-all duration-300"
                      style={{ width: `${item.score}%` }} // API에서 받은 score를 사용
                    />
                  </div>
                  <span className="text-xs text-muted-foreground min-w-[32px] text-right">
                    {item.score}
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
        
        <div className="mt-6 pt-4 border-t">
          <p className="text-xs text-muted-foreground text-center">
            키워드는 문서 내용 분석을 통해<br />
          자동으로 추출되었습니다
          </p>
        </div>
      </CardContent>
    </Card>
  );
}