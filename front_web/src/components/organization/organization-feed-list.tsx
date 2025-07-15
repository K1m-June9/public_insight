"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Bookmark } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useAuth } from "@/contexts/AuthContext";
import { useOrganizationFeedsQuery } from "@/hooks/queries/useFeedQueries";
import { useToggleBookmarkMutation } from "@/hooks/mutations/useFeedMutations";
import { OrganizationFeedItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";

interface OrganizationFeedListProps {
  organizationName: string;
  selectedCategoryId: number | null;
}

export default function OrganizationFeedList({ organizationName, selectedCategoryId }: OrganizationFeedListProps) {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [displayedFeeds, setDisplayedFeeds] = useState<OrganizationFeedItem[]>([]);

  const { data, isLoading, isError, isFetching } = useOrganizationFeedsQuery(organizationName, { 
    page, 
    limit: 20, 
    category_id: selectedCategoryId || undefined 
  });
  
  useEffect(() => {
    setPage(1);
    setDisplayedFeeds([]);
  }, [selectedCategoryId]);

  useEffect(() => {
    if (data?.data.feeds) {
      if (page === 1) {
        setDisplayedFeeds(data.data.feeds);
      } else {
        setDisplayedFeeds(prevFeeds => {
          const newFeeds = data.data.feeds.filter(
            newFeed => !prevFeeds.some(prevFeed => prevFeed.id === newFeed.id)
          );
          return [...prevFeeds, ...newFeeds];
        });
      }
    }
  }, [data, page]);

  const { mutate: toggleBookmark } = useToggleBookmarkMutation();
  
  const handleToggleBookmark = (e: React.MouseEvent, feedId: number) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) { alert("로그인이 필요한 서비스입니다."); return; }
    toggleBookmark(feedId);
  };
  
  const handleLoadMore = () => setPage(prevPage => prevPage + 1);
  const hasNextPage = data?.data.pagination.has_next ?? false;

  if (isLoading && page === 1) {
    return (
      <div className="space-y-6">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-gray-200 h-32 rounded-lg animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (isError) return <div className="text-center py-8 text-red-500">피드를 불러오는 중 오류가 발생했습니다.</div>;

  return (
    <div className="grid grid-cols-1 gap-6">
      {displayedFeeds.length === 0 && !isFetching ? (
        <div className="text-center py-8 text-gray-500">선택된 카테고리에 피드가 없습니다.</div>
      ) : (
        displayedFeeds.map((feed) => (
          <Link href={`/feed/${feed.id}`} key={feed.id} className="block">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-gray-400" onClick={(e) => handleToggleBookmark(e, feed.id)}>
                    <Bookmark className="h-5 w-5" />
                  </Button>
                </div>
                <div className="flex-grow">
                  <h3 className="font-medium text-lg mb-2">{feed.title}</h3>
                  <p className="text-gray-600 mb-3 line-clamp-3">{feed.summary}</p>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="text-xs bg-gray-100">{feed.category.name}</Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">{formatDate(feed.published_date)}</Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">조회 {feed.view_count}</Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">별점 {feed.average_rating.toFixed(1)}</Badge>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))
      )}
      {hasNextPage && (
        <div className="mt-4 text-center">
          <Button variant="outline" onClick={handleLoadMore} disabled={isFetching} className="w-full">
            {isFetching ? "로딩 중..." : "더보기"}
          </Button>
        </div>
      )}
    </div>
  );
}