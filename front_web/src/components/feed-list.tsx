"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, Star, Bookmark, ExternalLink } from "lucide-react";
import { useFeedsQuery } from "@/hooks/queries/useFeedQueries";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import { MainFeedItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";
import { formatNumber } from "@/lib/utils/format";

// 1. 피드 아이템을 위한 별도의 컴포넌트로 분리
interface FeedItemProps {
  feed: MainFeedItem;
}

function FeedItem({ feed }: FeedItemProps) {
  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-2">
          {/* organization.name을 카테고리 태그로 사용 */}
          <Badge variant="secondary">{feed.organization.name}</Badge>
          <div className="text-xs text-muted-foreground flex items-center gap-2">
            <span>{formatDate(feed.published_date)}</span>
            <Link href={`/feed/${feed.id}`} className="hover:text-primary"><ExternalLink className="h-4 w-4" /></Link>
          </div>
        </div>
        <Link href={`/feed/${feed.id}`}>
          <h3 className="text-lg font-semibold text-foreground hover:text-primary transition-colors mb-2 line-clamp-2">{feed.title}</h3>
        </Link>
        <p className="text-sm text-muted-foreground mb-4 line-clamp-3">{feed.summary}</p>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1"><Eye className="h-4 w-4" /><span>{formatNumber(feed.view_count)}</span></div>
          <div className="flex items-center gap-1"><Star className="h-4 w-4" /><span>{feed.average_rating.toFixed(1)}</span></div>
          <div className="flex items-center gap-1"><Bookmark className="h-4 w-4" /><span>{feed.bookmark_count}</span></div>
        </div>
      </CardContent>
    </Card>
  );
}

// 2. 메인 FeedList 컴포넌트 (페이지네이션 로직 포함)
export function FeedList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  // URL에서 현재 페이지 번호를 읽어옴
  const currentPage = Number(searchParams.get('page')) || 1;

  const { data: feedData, isLoading, isError } = useFeedsQuery({ page: currentPage, limit: 10 }); // 페이지당 10개씩

  const feeds = feedData?.data.feeds || [];
  const pagination = feedData?.data.pagination;

  const handlePageChange = (page: number) => {
    // 페이지 변경 시 URL 쿼리 파라미터를 업데이트
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    current.set('page', String(page));
    // 현재 페이지가 메인('/')이므로, 쿼리 파라미터만 추가
    router.push(`/?${current.toString()}`);
  };
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => <div key={i} className="bg-gray-200 h-40 rounded-lg animate-pulse"></div>)}
      </div>
    );
  }

  if (isError) {
    return <div className="text-center py-8 text-red-500">피드를 불러오는 중 오류가 발생했습니다.</div>;
  }

  return (
    <section>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-primary">최신 소식</h2>
      </div>
      
      <div className="space-y-4">
        {feeds.map((feed) => (
          <FeedItem key={feed.id} feed={feed} />
        ))}
      </div>
      
      {pagination && pagination.total_pages > 1 && (
        <div className="mt-8 flex justify-center">
          <Pagination>
            <PaginationContent>
              <PaginationItem>
                <PaginationPrevious onClick={() => handlePageChange(Math.max(1, currentPage - 1))} className={currentPage === 1 ? "pointer-events-none opacity-50" : "cursor-pointer"} />
              </PaginationItem>
              
              {/* 페이지 번호 렌더링 (간단한 버전) */}
              {Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map((page) => (
                <PaginationItem key={page}>
                  <PaginationLink onClick={() => handlePageChange(page)} isActive={currentPage === page} className="cursor-pointer">{page}</PaginationLink>
                </PaginationItem>
              ))}
              
              <PaginationItem>
                <PaginationNext onClick={() => handlePageChange(Math.min(pagination.total_pages, currentPage + 1))} className={currentPage === pagination.total_pages ? "pointer-events-none opacity-50" : "cursor-pointer"} />
              </PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </section>
  );
}