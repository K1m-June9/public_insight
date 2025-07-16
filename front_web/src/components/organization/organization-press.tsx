// 파일 위치: components/organization/organization-press.tsx

"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { usePressReleasesQuery } from "@/hooks/queries/useFeedQueries";
import { PressReleaseItem } from "@/lib/types/feed";
import { formatDate } from "@/lib/utils/date";

interface OrganizationPressProps {
  organizationName: string;
}

export default function OrganizationPress({ organizationName }: OrganizationPressProps) {
  const [page, setPage] = useState(1);
  const [displayedReleases, setDisplayedReleases] = useState<PressReleaseItem[]>([]);
  const { data, isLoading, isError, isFetching } = usePressReleasesQuery(organizationName, { page, limit: 15 });

  useEffect(() => {
    if (data?.data.press_releases) {
      setDisplayedReleases(prev => {
        const newItems = data.data.press_releases.filter(
          newItem => !prev.some(prevItem => prevItem.id === newItem.id)
        );
        return page === 1 ? data.data.press_releases : [...prev, ...newItems];
      });
    }
  }, [data, page]);

  const handleLoadMore = () => setPage(prev => prev + 1);
  const hasNextPage = data?.data.pagination.has_next ?? false;

  if (isLoading && page === 1) {
    return <div className="bg-gray-200 h-[400px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }
  
  if (isError) return <div className="text-center py-8 text-red-500">보도자료를 불러오는 중 오류가 발생했습니다.</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-900">{organizationName} 보도자료</h2>
      {displayedReleases.length === 0 && !isFetching ? (
        <div className="text-center py-8 text-gray-500">등록된 보도자료가 없습니다.</div>
      ) : (
        <div className="space-y-4">
          {displayedReleases.map((release) => (
            <Link href={`/feed/${release.id}`} key={release.id} className="block">
              <div className="bg-gray-50 p-4 rounded-md border border-gray-100 hover:bg-gray-100 transition-colors">
                <h3 className="font-medium text-lg mb-2">{release.title}</h3>
                <p className="text-gray-600 mb-3 line-clamp-2">{release.summary}</p>
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs bg-gray-50">{formatDate(release.published_date)}</Badge> {/*놓쳐서 오류생긴 부분 시발시발시발시발, 일단은 수정 완료*/}
                </div>
              </div>
            </Link>
          ))}
        </div>
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