"use client";

import React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation"; 
import { Clock, ExternalLink, Eye, Star, Bookmark } from "lucide-react";

import { useOrganizationFeedsQuery } from "@/hooks/queries/useFeedQueries";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import { OrganizationFeedItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";
import { formatNumber } from "@/lib/utils/format";

// 1. 개별 피드 카드 UI를 위한 별도 컴포넌트 (Figma proto2.tsx 참고)
function FeedCard({ feed }: { feed: OrganizationFeedItem }) {

  // 별점 렌더링을 위한 헬퍼 함수
  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    return (
      <div className="flex items-center space-x-0.5">
        {[...Array(5)].map((_, i) => {
          if (i < fullStars) {
            return <Star key={i} className="w-3 h-3 text-yellow-400 fill-current" />;
          } else if (i === fullStars && hasHalfStar) {
            // 반쪽 별을 CSS로 구현 (더 간단하고 안정적)
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
    // Card 대신 article 태그와 group 클래스를 사용하여 feed-list.tsx와 동일한 구조를 만듭니다.
    <article className="group p-6 rounded-lg border bg-card border-border hover:border-primary/30 hover:shadow-lg hover:translate-x-1 transition-all duration-300 cursor-pointer">
      <div className="flex items-start justify-between mb-4">
        <Badge variant="secondary">{feed.category.name}</Badge>
        <div className="flex items-center text-xs text-muted-foreground">
          <Clock className="w-3 h-3 mr-1" />
          {formatDate(feed.published_date)}
        </div>
      </div>
      
      <div className="flex items-start space-x-4">
        <div className="flex-1 min-w-0">
          <Link href={`/feed/${feed.id}`} className="block">
            <h3 className="mb-3 leading-tight text-foreground group-hover:text-primary transition-colors duration-300 line-clamp-2">
              {feed.title}
            </h3>
            <p className="text-sm text-muted-foreground mb-4 leading-relaxed line-clamp-2">
              {feed.summary}
            </p>
          </Link>
        </div>
        
        <Link href={`/feed/${feed.id}`} className="flex-shrink-0 mt-1" target="_blank" rel="noopener noreferrer">
          <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors duration-300" />
        </Link>
      </div>

      <div className="flex items-center justify-end space-x-4">
        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
          <Eye className="w-3 h-3" />
          <span>{formatNumber(feed.view_count)}</span>
        </div>
        <div className="flex items-center space-x-1">
          {renderStars(feed.average_rating)}
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
  };

// 2. 메인 목록 및 페이지네이션 컨테이너
interface OrganizationFeedListProps {
  organizationName: string;
  selectedCategoryId: number | null;
}

export default function OrganizationFeedList({ organizationName, selectedCategoryId }: OrganizationFeedListProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const currentPage = Number(searchParams.get('page')) || 1;

  const { data, isLoading, isError } = useOrganizationFeedsQuery(organizationName, {
    page: currentPage,
    limit: 6,
    category_id: selectedCategoryId || undefined,
  });

  const feeds = data?.data.feeds || [];
  const pagination = data?.data.pagination;

  const handlePageChange = (page: number) => {
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    current.set('page', String(page));
    router.push(`?${current.toString()}`);
  };

  // feed-list.tsx와 동일한 페이지네이션 헬퍼 함수
  const getPageNumbers = () => {
    if (!pagination) return [];
    const totalPages = pagination.total_pages;
    const maxPagesToShow = 5;
    const pages = [];

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
    } else {
      let startPage = Math.max(1, currentPage - 2);
      let endPage = Math.min(totalPages, currentPage + 2);
      if (currentPage < 3) {
        startPage = 1;
        endPage = 5;
      } else if (currentPage > totalPages - 2) {
        startPage = totalPages - 4;
        endPage = totalPages;
      }
      for (let i = startPage; i <= endPage; i++) pages.push(i);
    }
    return pages;
  };

  const pageNumbers = getPageNumbers();
  
  if (isLoading) {
    return (
        <div className="space-y-4">
            {[...Array(5)].map((_, i) => <div key={i} className="bg-gray-200 h-48 rounded-lg animate-pulse"></div>)}
        </div>
    );
  }

  if (isError) {
    return <div className="text-center py-8 text-red-500">피드를 불러오는 중 오류가 발생했습니다.</div>;
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4">
        {feeds.length > 0 ? (
          feeds.map((feed) => <FeedCard key={feed.id} feed={feed} />)
        ) : (
          <div className="text-center py-16 text-muted-foreground">
            {selectedCategoryId ? "선택된 카테고리에 피드가 없습니다." : "표시할 정책 문서가 없습니다."}
          </div>
        )}
      </div>
      
      {pagination && pagination.total_pages > 1 && (
        <div className="flex justify-center mt-6">
          <Pagination>
            <PaginationContent>
              <PaginationItem><PaginationPrevious onClick={() => handlePageChange(Math.max(1, currentPage - 1))} className={!pagination.has_previous ? "pointer-events-none opacity-50" : "cursor-pointer"} /></PaginationItem>
              
              {/* 페이지 번호 렌더링 부분을 수정된 로직으로 교체 */}
              {pageNumbers.map((page) => (
                <PaginationItem key={page}><PaginationLink onClick={() => handlePageChange(page)} isActive={currentPage === page} className="cursor-pointer">{page}</PaginationLink></PaginationItem>
              ))}
              
              <PaginationItem><PaginationNext onClick={() => handlePageChange(Math.min(pagination.total_pages, currentPage + 1))} className={!pagination.has_next ? "pointer-events-none opacity-50" : "cursor-pointer"} /></PaginationItem>
            </PaginationContent>
          </Pagination>
        </div>
      )}
    </div>
  );
}