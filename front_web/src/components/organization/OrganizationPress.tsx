"use client";

import React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Clock, ExternalLink, Eye, Star, Bookmark, Newspaper } from "lucide-react";
import { usePressReleasesQuery } from "@/hooks/queries/useFeedQueries";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import { PressReleaseItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";
import { formatNumber } from "@/lib/utils/format";

// 1. 개별 보도자료 카드 UI를 위한 별도 컴포넌트
function PressCard({ feed }: { feed: PressReleaseItem }) {
  
  // 💡 반쪽 별 렌더링 함수 (OrganizationFeedList와 동일)
  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    return (
      <div className="flex items-center space-x-0.5">
        {[...Array(5)].map((_, i) => {
          if (i < fullStars) {
            return <Star key={i} className="w-3 h-3 text-yellow-400 fill-current" />;
          } else if (i === fullStars && hasHalfStar) {
            return (
              <div key={i} className="relative">
                <Star className="w-3 h-3 text-gray-300" />
                <div className="absolute top-0 left-0 h-full w-1/2 overflow-hidden">
                  <Star className="w-3 h-3 text-yellow-400 fill-current" />
                </div>
              </div>
            );
          } else {
            return <Star key={i} className="w-3 h-3 text-gray-300" />;
          }
        })}
      </div>
    );
  };

  return (
    <Card className="group hover:border-primary/30 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-3">
          {/* 보도자료는 카테고리가 항상 '보도자료'이므로, 뱃지는 생략하거나 고정할 수 있습니다. */}
          <Badge variant="secondary">{feed.category.name}</Badge>
          <div className="flex items-center text-xs text-muted-foreground gap-1"><Clock className="h-3 w-3" /><span>{formatDate(feed.published_date)}</span></div>
        </div>
        
        <div className="flex items-start space-x-4">
          <div className="flex-1 min-w-0">
            <Link href={`/feed/${feed.id}`} className="block">
              <h3 className="font-semibold text-foreground group-hover:text-primary transition-colors mb-2 line-clamp-2 leading-snug">{feed.title}</h3>
              <p className="text-sm text-muted-foreground mb-4 leading-relaxed line-clamp-2">{feed.summary}</p>
            </Link>
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1"><Eye className="h-4 w-4" /><span>{formatNumber(feed.view_count)}</span></div>
                    <div className="flex items-center gap-1">{renderStars(feed.average_rating)}<span className="ml-1">{feed.average_rating.toFixed(1)}</span></div>
                    <div className="flex items-center gap-1"><Bookmark className="h-4 w-4" /><span>{feed.bookmark_count}</span></div>
                </div>
                <Link href={`/feed/${feed.id}`}><ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-primary" /></Link>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// 2. 메인 목록 및 페이지네이션 컨테이너
interface OrganizationPressProps {
  organizationName: string;
}

export default function OrganizationPress({ organizationName }: OrganizationPressProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = Number(searchParams.get('press_page')) || 1; // 💡 페이지 파라미터 이름 변경

  const { data, isLoading, isError } = usePressReleasesQuery(organizationName, {
    page: currentPage,
    limit: 10,
  });

  const releases = data?.data.press_releases || [];
  const pagination = data?.data.pagination;

  const handlePageChange = (page: number) => {
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    current.set('press_page', String(page)); // 💡 페이지 파라미터 이름 변경
    router.push(`?${current.toString()}`);
  };
  
  if (isLoading) {
    return <div className="space-y-4">{[...Array(3)].map((_, i) => <div key={i} className="bg-gray-200 h-40 rounded-lg animate-pulse"></div>)}</div>;
  }

  if (isError) {
    return <div className="text-center py-8 text-red-500">보도자료를 불러오는 중 오류가 발생했습니다.</div>;
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-primary">보도자료</h2>
      <div className="space-y-4">
        {releases.length > 0 ? (
          releases.map((release) => <PressCard key={release.id} feed={release} />)
        ) : (
          <div className="text-center py-16 text-muted-foreground">
            <Newspaper className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>등록된 보도자료가 없습니다.</p>
          </div>
        )}
      </div>
      
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center mt-6">
            <Pagination>
                <PaginationContent>
                    {/* ... (페이지네이션 JSX) */}
                </PaginationContent>
            </Pagination>
        </div>
      )}
    </div>
  );
}