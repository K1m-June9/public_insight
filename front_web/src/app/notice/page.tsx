"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import { useNoticesQuery } from "@/hooks/queries/useNoticeQueries";
import { Button } from "@/components/ui/button";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { NoticeListItem } from "@/lib/types/notice";
import { formatDate } from "@/lib/utils/date";

export default function NoticeListPage() {
  const router = useRouter();

  const [page, setPage] = useState(1);
  const [displayedNotices, setDisplayedNotices] = useState<NoticeListItem[]>([]);
  const { data, isLoading, isError, isFetching } = useNoticesQuery({ page, limit: 10 }); // 한 페이지에 10개씩

  useEffect(() => {
    if (data?.data.notices) {
      if (page === 1) {
        setDisplayedNotices(data.data.notices);
      } else {
        setDisplayedNotices(prev => {
          const newItems = data.data.notices.filter(
            newItem => !prev.some(prevItem => prevItem.id === newItem.id)
          );
          return [...prev, ...newItems];
        });
      }
    }
  }, [data, page]);
  
  const handleLoadMore = () => setPage(prev => prev + 1);
  const hasNextPage = data?.data.pagination.has_next ?? false;

  const goBack = () => router.back();

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <div className="max-w-3xl mx-auto">
            <Button variant="ghost" onClick={goBack} className="mb-6 flex items-center gap-1"><ArrowLeft className="h-4 w-4" /><span>뒤로가기</span></Button>
            <h1 className="text-2xl font-bold mb-6 text-gray-900">공지사항</h1>

            {isLoading && page === 1 ? (
              <div className="text-center py-8">로딩 중...</div>
            ) : isError ? (
              <div className="text-center py-8 text-red-500">오류가 발생했습니다.</div>
            ) : (
              <div className="space-y-4">
                {displayedNotices.map((notice) => (
                  <Link href={`/notice/${notice.id}`} key={notice.id} className="block">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                      {/* API 응답에는 preview가 없으므로 title과 date만 표시합니다. */}
                      <div className="flex justify-between items-center">
                        <h2 className="text-lg font-medium">{notice.title}</h2>
                        <span className="text-sm text-gray-500 flex-shrink-0 ml-4">{formatDate(notice.created_at)}</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            {hasNextPage && (
              <div className="mt-8 text-center">
                <Button variant="outline" onClick={handleLoadMore} disabled={isFetching} className="w-full">
                  {isFetching ? "로딩 중..." : "더보기"}
                </Button>
              </div>
            )}
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}