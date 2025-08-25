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
        // 스켈레톤 UI (Figma 디자인 구조에 맞게 수정)
        <div className="animate-pulse">
          <div className="border-b border-border bg-card">
            <div className="max-w-4xl mx-auto px-4 py-6">
              <div className="h-8 w-24 bg-gray-200 rounded-md mb-6"></div>
              <div className="space-y-3">
                <div className="h-8 w-3/4 bg-gray-200 rounded-md"></div>
                <div className="h-5 w-1/2 bg-gray-200 rounded-md"></div>
              </div>
            </div>
          </div>
          <main className="max-w-4xl mx-auto px-4 py-8">
            <div className="bg-gray-200 h-96 rounded-lg"></div>
          </main>
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
      <div>
        {/* 헤더 영역 */}
        <div className="border-b border-border bg-card">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <div className="flex items-center mb-6">
              <Button variant="ghost" size="sm" onClick={goBack} className="flex items-center space-x-2 text-muted-foreground">
                <ArrowLeft className="w-4 h-4" />
                <span>목록으로</span>
              </Button>
            </div>
            <div className="space-y-4">
              <h1 className="text-2xl leading-tight text-foreground">{notice.title}</h1>
              <div className="flex items-center space-x-6 text-sm text-muted-foreground">
                <div className="flex items-center space-x-2"><User className="w-4 h-4" /><span>{notice.author}</span></div>
                <div className="flex items-center space-x-2"><Calendar className="w-4 h-4" /><span>{formatDate(notice.created_at)}</span></div>
              </div>
            </div>
          </div>
        </div>

        {/* 메인 콘텐츠 영역 */}
        <main className="max-w-4xl mx-auto px-4 py-8">
          <Card>
            <CardContent className="p-8">
              {/* --- 💡 2단계: 문단 구분을 위해 콘텐츠 렌더링 방식을 개선합니다. --- 
              <div className="prose max-w-none">
                {notice.content.split('\n\n').map((paragraph, index) => (
                  <p key={index} className="mb-6 leading-relaxed text-foreground">
                    {paragraph}
                  </p>
                ))}
              </div>
              */}
              <div className="prose max-w-none"dangerouslySetInnerHTML={{ __html: notice.content }} />
            </CardContent>
          </Card>
        </main>
      </div>
    );
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-background">
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