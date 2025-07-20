"use client";

import React, { useState, useEffect } from "react";
import { Bookmark } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useFeedsQuery } from "@/hooks/queries/useFeedQueries";
import { useToggleBookmarkMutation } from "@/hooks/mutations/useFeedMutations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { MainFeedItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";

export function FeedList() {
  const { user } = useAuth();
  
  // 1. 페이지 번호와 누적된 피드 목록을 위한 state 생성
  const [page, setPage] = useState(1);
  const [displayedFeeds, setDisplayedFeeds] = useState<MainFeedItem[]>([]);

  // 2. 현재 페이지 번호로 데이터를 가져오는 useFeedsQuery 호출
  const { data, isLoading, isError, isFetching } = useFeedsQuery({ page, limit: 20 });
  
  // 3. useFeedsQuery가 새로운 데이터를 가져올 때마다 누적 목록에 추가
  useEffect(() => {
    // data가 존재하고, 새로운 데이터가 있다면 (중복 추가 방지)
    if (data?.data.feeds) {
      // 새로운 피드 목록만 추가합니다.
      // 이전에 불러온 페이지의 데이터가 중복으로 추가되는 것을 방지합니다.
      setDisplayedFeeds(prevFeeds => {
        const newFeeds = data.data.feeds.filter(
          newFeed => !prevFeeds.some(prevFeed => prevFeed.id === newFeed.id)
        );
        return [...prevFeeds, ...newFeeds];
      });
    }
  }, [data]);

  const { mutate: toggleBookmark, isPending: isTogglingBookmark } = useToggleBookmarkMutation();

  const handleToggleBookmark = (e: React.MouseEvent, feedId: number) => {
    e.preventDefault();
    e.stopPropagation();

    if (!user) {
      alert("로그인이 필요한 서비스입니다.");
      return;
    }
    toggleBookmark(feedId);
  };
  
  const handleLoadMore = () => {
    setPage(prevPage => prevPage + 1);
  };

  const hasNextPage = data?.data.pagination.has_next ?? false;

  // 초기 로딩 (첫 페이지를 불러올 때)
  if (isLoading && page === 1) {
    return (
      <div className="mt-8 space-y-6">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="bg-gray-200 h-32 rounded-lg animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (isError) {
    return <div className="mt-8 text-center text-red-500">피드를 불러오는 중 오류가 발생했습니다.</div>;
  }

  return (
    <div className="mt-8">
      <div className="grid grid-cols-1 gap-6">
        {displayedFeeds.map((feed) => (
          <Link href={`/feed/${feed.id}`} key={feed.id} className="block">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex gap-4">
                <div className="flex-shrink-0">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-gray-400"
                    onClick={(e) => handleToggleBookmark(e, feed.id)}
                    disabled={isTogglingBookmark}
                  >
                    <Bookmark className="h-5 w-5" />
                  </Button>
                </div>
                <div className="flex-grow">
                  <h3 className="font-medium text-lg mb-2">{feed.title}</h3>
                  <p className="text-gray-600 mb-3 line-clamp-3">{feed.summary}</p>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline" className="text-xs bg-gray-100">
                      {feed.organization.name}
                    </Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">
                      {formatDate(feed.published_date)}
                    </Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">
                      조회 {feed.view_count}
                    </Badge>
                    <Badge variant="outline" className="text-xs bg-gray-50">
                      별점 {feed.average_rating.toFixed(1)}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* 더보기 버튼 */}
      <div className="mt-8 text-center">
        <Button
          variant="outline"
          onClick={handleLoadMore}
          disabled={!hasNextPage || isFetching}
          className="w-full"
        >
          {isFetching
            ? "로딩 중..."
            : hasNextPage
            ? "더보기"
            : "마지막 피드입니다"}
        </Button>
      </div>
    </div>
  );
}