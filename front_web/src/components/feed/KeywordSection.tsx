"use client";

import Link from "next/link"; // 1. 페이지 이동을 위해 Link 컴포넌트를 임포트
import { useRelatedKeywordsQuery } from "@/hooks/queries/useGraphQueries"; // 2. 우리가 만든 커스텀 훅을 임포트
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"; // 3. 더 나은 구조를 위해 Card 컴포넌트 활용
import { Sparkles } from "lucide-react"; // 4. '인사이트'의 의미를 담은 아이콘

interface KeywordSectionProps {
  feedId: number; // 5. 이제 feedId는 필수로 받음
}

export default function KeywordSection({ feedId }: KeywordSectionProps) {
  // 6. TanStack Query 훅을 호출하여 서버 상태를 가져옴
  const { data: response, isLoading, isError } = useRelatedKeywordsQuery(feedId, {
    // feedId가 유효한 숫자일 때만 쿼리가 실행되도록 보장
    enabled: !!feedId && feedId > 0,
    // 이 컴포넌트에서는 7개의 키워드를 요청
    limit: 7,
  });

  // 7. API 응답에서 실제 데이터 배열을 추출 (없으면 빈 배열)
  const keywords = response?.data || [];

  // --- 8. 로딩 상태 UI ---
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

  // --- 9. 에러 상태 UI ---
  if (isError) {
    // 에러가 발생하면 컴포넌트 자체를 렌더링하지 않음 (선택적)
    // 또는 에러 메시지를 보여줄 수 있음
    return null;
  }
  
  // --- 10. 데이터가 없는 경우 UI ---
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

  // --- 11. 성공 상태 UI ---
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