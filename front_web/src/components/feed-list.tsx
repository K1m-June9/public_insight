"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Eye, Star, Bookmark, ExternalLink, Clock } from "lucide-react";
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
  // 별점 렌더링 함수를 FeedList에서 이곳으로 이동시킵니다.
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
                <Star className="w-3 h-3 text-muted" />
                <div className="absolute inset-0 overflow-hidden w-1/2">
                  <Star className="w-3 h-3 text-yellow-400 fill-current" />
                </div>
              </div>
            );
          } else {
            return <Star key={i} className="w-3 h-3 text-muted" />;
          }
        })}
      </div>
    );
  };

  return (
    // Card 대신 article 태그와 group 클래스를 사용하여 디자인과 동일한 구조를 만듭니다.
    <article className="group p-6 rounded-lg border bg-card border-border hover:border-primary/30 hover:shadow-lg hover:translate-x-1 transition-all duration-300 cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <Badge variant="secondary">{feed.organization.name}</Badge>
        <div className="flex items-center text-xs text-muted-foreground">
          <Clock className="w-3 h-3 mr-1" />
          {formatDate(feed.published_date)}
        </div>
      </div>
      
      <div className="flex items-start space-x-4">
        {/* Link로 제목과 요약을 감싸서 클릭 영역을 만듭니다. */}
        <Link href={`/feed/${feed.id}`} className="flex-1 min-w-0">
          <h3 className="mb-3 leading-tight text-foreground group-hover:text-primary transition-colors duration-300">
            {feed.title}
          </h3>
          <p className="text-sm text-muted-foreground mb-4 leading-relaxed line-clamp-2">
            {feed.summary}
          </p>
        </Link>
        
        {/* 외부 링크 아이콘을 오른쪽으로 분리합니다. */}
        <Link href={`/feed/${feed.id}`} className="flex-shrink-0" target="_blank" rel="noopener noreferrer">
          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors duration-300" />
        </Link>
      </div>

      {/* 통계 섹션 (우측 정렬) */}
      <div className="flex items-center justify-end space-x-4">
        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
          <Eye className="w-3 h-3" />
          <span>{formatNumber(feed.view_count)}</span>
        </div>
        <div className="flex items-center space-x-1">
          {renderStars(feed.average_rating)} {/* 💡 renderStars 함수 호출 */}
          <span className="text-xs text-muted-foreground ml-1">
            {feed.average_rating.toFixed(1)}
          </span>
        </div>
        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
          <Bookmark className="w-3 h-3" />
          <span>{feed.bookmark_count}</span>
        </div>
      </div>
    </article>
  );
}

// 2. 메인 FeedList 컴포넌트 (페이지네이션 로직 포함)
export function FeedList() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = Number(searchParams.get('page')) || 1;
  const { data: feedData, isLoading, isError } = useFeedsQuery({ page: currentPage, limit: 5 });

  const feeds = feedData?.data.feeds || [];
  const pagination = feedData?.data.pagination;

  // --- 💡 2단계: 여기 있던 renderStars 함수는 FeedItem으로 이동했으므로 삭제합니다. ---

  const handlePageChange = (page: number) => {
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    current.set('page', String(page));
    router.push(`/?${current.toString()}`);
  };

  const getPageNumbers = () => {
    if (!pagination) return [];

    const totalPages = pagination.total_pages;
    const maxPagesToShow = 5; // 화면에 보여줄 최대 페이지 수
    const pages = [];

    if (totalPages <= maxPagesToShow) {
      // 전체 페이지가 5개 이하이면 모든 페이지 번호를 보여줌
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // 전체 페이지가 5개를 초과할 경우
      let startPage = Math.max(1, currentPage - 2);
      let endPage = Math.min(totalPages, currentPage + 2);

      // 현재 페이지를 중심으로 양옆에 2개씩 보여주도록 조정
      if (currentPage < 3) {
        startPage = 1;
        endPage = 5;
      } else if (currentPage > totalPages - 2) {
        startPage = totalPages - 4;
        endPage = totalPages;
      }
      
      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
    }
    return pages;
  };

  const pageNumbers = getPageNumbers();

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
        <h2 className="text-lg font-medium text-primary">최신 소식</h2>
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
              
              {/* --- 💡 2단계: 페이지 번호 렌더링 부분을 수정합니다. --- */}
              {pageNumbers.map((page) => (
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