"use client";

import React, { useState } from "react"; // 💡 useState를 import 합니다.
import Link from "next/link";
import { useRouter } from "next/navigation"; // 💡 useSearchParams는 더 이상 필요 없으므로 제거합니다.
import { ArrowLeft, Bell, Calendar } from "lucide-react";
import { useNoticesQuery } from "@/hooks/queries/useNoticeQueries";
import { Button } from "@/components/ui/button";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { formatDate } from "@/lib/utils/date";

export default function NoticeListPage() {
  const router = useRouter();
  
  // --- 💡 1단계: useSearchParams 대신 useState를 사용하여 페이지 상태를 관리합니다. ---
  const [currentPage, setCurrentPage] = useState(1);

  // useNoticesQuery는 이제 URL이 아닌, useState의 currentPage를 사용합니다.
  const { data: noticeData, isLoading, isError } = useNoticesQuery({ page: currentPage, limit: 6 });

  const notices = noticeData?.data.notices || [];
  const pagination = noticeData?.data.pagination;

  // --- 💡 2단계: handlePageChange 함수가 더 이상 URL을 변경하지 않고, 내부 상태(currentPage)만 변경하도록 수정합니다. ---
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const goBack = () => router.back();

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

  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Header />
      <main className="flex-grow">
        {/* 헤더 섹션 (기존과 동일) */}
        <div className="border-b border-border bg-card">
            <div className="container max-w-4xl mx-auto px-4 py-6">
                <Button variant="ghost" size="sm" onClick={goBack} className="flex items-center space-x-2 mb-6 text-muted-foreground"><ArrowLeft className="w-4 h-4" /><span>메인으로</span></Button>
                <div className="space-y-2">
                    <div className="flex items-center space-x-3"><Bell className="w-6 h-6 text-primary" /><h1 className="text-2xl font-bold leading-tight text-foreground">공지사항</h1></div>
                    <p className="text-muted-foreground">PublicInsight의 최신 소식과 업데이트를 확인하세요</p>
                </div>
            </div>
        </div>
        
        {/* 콘텐츠 섹션 (기존과 동일) */}
        <div className="container max-w-4xl mx-auto px-4 py-8">
            <div className="flex items-center justify-between mb-6">
                <div className="text-sm text-muted-foreground">
                    총 {pagination?.total_count || 0}개의 공지사항
                </div>
            </div>

            {isLoading ? (<div className="text-center py-8">로딩 중...</div>)
            : isError ? (<div className="text-center py-8 text-red-500">오류가 발생했습니다.</div>)
            : (
                <div className="space-y-4 mb-8">
                    {notices.map((notice) => (
                    <Link 
                      href={`/notice/${notice.id}`} 
                      key={notice.id} 
                      className="block group bg-card border border-border rounded-lg p-6 hover:shadow-md transition-all"
                    >
                      <div className="flex items-center justify-between">
                          <h3 className="group-hover:text-primary transition-colors">{notice.title}</h3>
                          <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                          <Calendar className="w-3 h-3" />
                          <span>{formatDate(notice.created_at)}</span>
                          </div>
                      </div>
                    </Link>
                    ))}
                </div>
            )}

            {pagination && pagination.total_pages > 1 && (
            <div className="flex justify-center">
                <Pagination>
                    <PaginationContent>
                        {/* 페이지네이션 컴포넌트들은 이제 URL 대신 내부 상태를 변경하는 handlePageChange를 호출합니다. */}
                        <PaginationItem><PaginationPrevious onClick={() => handlePageChange(Math.max(1, currentPage - 1))} className={!pagination.has_previous ? "pointer-events-none opacity-50" : "cursor-pointer"} /></PaginationItem>
                        {pageNumbers.map((page) => (
                            <PaginationItem key={page}><PaginationLink onClick={() => handlePageChange(page)} isActive={currentPage === page} className="cursor-pointer">{page}</PaginationLink></PaginationItem>
                        ))}
                        <PaginationItem><PaginationNext onClick={() => handlePageChange(Math.min(pagination.total_pages, currentPage + 1))} className={!pagination.has_next ? "pointer-events-none opacity-50" : "cursor-pointer"} /></PaginationItem>
                    </PaginationContent>
                </Pagination>
            </div>
            )}
        </div>
      </main>
      <Footer />
    </div>
  );
}