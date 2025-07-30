"use client";

import { useRouter, useParams } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useNoticeDetailQuery } from "@/hooks/queries/useNoticeQueries";
import { Button } from "@/components/ui/button";
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

  if (isLoading) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <main className="flex-grow"><div className="container px-4 py-8 md:px-6"><div className="flex justify-center items-center h-[60vh]"><div className="animate-pulse text-gray-500">로딩 중...</div></div></div></main>
        <Footer />
      </div>
    );
  }

  if (isError || !notice) {
    return (
      <div className="flex flex-col min-h-screen bg-gray-50">
        <Header />
        <main className="flex-grow"><div className="container px-4 py-8 md:px-6"><div className="flex flex-col justify-center items-center h-[60vh] gap-4"><p className="text-gray-500">공지사항을 찾을 수 없습니다.</p><Button variant="outline" onClick={() => router.push('/notice')}>목록으로 돌아가기</Button></div></div></main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <div className="max-w-3xl mx-auto">
            <Button variant="ghost" onClick={goBack} className="mb-6 flex items-center gap-1"><ArrowLeft className="h-4 w-4" /><span>뒤로가기</span></Button>
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
              <h1 className="text-2xl font-bold mb-4 text-gray-900">{notice.title}</h1>
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
                <span className="text-gray-600">{notice.author}</span>
                <span className="text-sm text-gray-500">{formatDate(notice.created_at)}</span>
              </div>
              {/*<div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: notice.content }} />*/}
              <div className="prose max-w-none">
                <p className="whitespace-pre-wrap">{notice.content}</p>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}