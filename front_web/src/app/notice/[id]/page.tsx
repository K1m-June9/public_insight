"use client";

import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, User, Calendar } from "lucide-react";
import { useNoticeDetailQuery } from "@/hooks/queries/useNoticeQueries";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { formatDate } from "@/lib/utils/date";

export default function NoticeDetailPage() {
  const router = useRouter();
  const params = useParams();
  const noticeId = Number(params.id);

  const { data: noticeData, isLoading, isError } = useNoticeDetailQuery(noticeId, {
    enabled: !isNaN(noticeId) && noticeId > 0,
  });

  const notice = noticeData?.data.notice;
  const goBack = () => router.back();

  const renderContent = () => {
    if (isLoading) {
      // 로딩 스켈레톤 UI
      return (
        <div className="max-w-4xl mx-auto animate-pulse">
          <div className="h-8 w-24 bg-gray-200 rounded-md mb-8"></div>
          <div className="space-y-4 mb-6">
            <div className="h-10 w-3/4 bg-gray-200 rounded-md"></div>
            <div className="h-6 w-1/2 bg-gray-200 rounded-md"></div>
          </div>
          <div className="bg-gray-200 h-96 rounded-lg"></div>
        </div>
      );
    }

    if (isError || !notice) {
      // 에러 UI
      return (
        <div className="text-center py-16">
          <p className="text-muted-foreground mb-4">공지사항을 찾을 수 없습니다.</p>
          <Button variant="outline" onClick={() => router.push('/notice')}>목록으로 돌아가기</Button>
        </div>
      );
    }

    // 실제 콘텐츠 UI
    return (
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center mb-6">
          <Button variant="ghost" size="sm" onClick={goBack} className="flex items-center space-x-2 text-muted-foreground">
            <ArrowLeft className="w-4 h-4" />
            <span>목록으로</span>
          </Button>
        </div>
        <div className="space-y-4 mb-8">
          <h1 className="text-3xl font-bold leading-tight text-foreground">{notice.title}</h1>
          <div className="flex items-center space-x-6 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2"><User className="w-4 h-4" /><span>{notice.author}</span></div>
            <div className="flex items-center space-x-2"><Calendar className="w-4 h-4" /><span>{formatDate(notice.created_at)}</span></div>
          </div>
        </div>
        <Card>
          <CardContent className="p-8">
            {/* 평문 텍스트 + 줄바꿈 유지 방식 */}
            <div className="prose max-w-none">
              <p className="whitespace-pre-wrap">{notice.content}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          {renderContent()}
        </div>
      </main>
      <Footer />
    </div>
  );
}