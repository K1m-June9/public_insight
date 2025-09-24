"use client";

import { useRouter, useParams } from "next/navigation";
import dynamic from 'next/dynamic'; // 1. next/dynamic을 임포트
import { ArrowLeft, Bookmark, Scroll, Share2, Star } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useFeedDetailQuery } from "@/hooks/queries/useFeedQueries";
import { useToggleBookmarkMutation, usePostRatingMutation } from "@/hooks/mutations/useFeedMutations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/date";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { ScrollToTopButton } from "@/components/ScrollToTop"
import { FeedRecommendations } from "@/components/feed/FeedRecommendations";

// 2. PdfViewer 컴포넌트를 dynamic import
const PdfViewer = dynamic(() => import('@/components/PdfViewer').then(mod => mod.PdfViewer), {
  ssr: false, // 서버 사이드 렌더링을 비활성화
  loading: () => <div className="text-center p-10">PDF 뷰어를 불러오는 중...</div>,
});


export default function FeedDetailPage() {
  const router = useRouter();
  const params = useParams();
  const feedId = Number(params.id);

  const { user } = useAuth();

  const { data: feedData, isLoading, isError } = useFeedDetailQuery(feedId, {
    enabled: !isNaN(feedId) && feedId > 0,
  });
  
  const { mutate: toggleBookmark } = useToggleBookmarkMutation();
  const { mutate: postRating } = usePostRatingMutation();

  const feed = feedData?.data.feed;
  const isBookmarked = feed?.is_bookmarked ?? false;
  const userRating = feed?.user_rating ?? 0;

  // ... (handleToggleBookmark, handleRating 등 다른 함수들은 이전과 동일)
  const handleToggleBookmark = () => {
    if (!user) { alert("로그인이 필요한 서비스입니다."); return; }
    toggleBookmark(feedId);
  };

  const handleRating = (rating: number) => {
    if (!user) { alert("로그인이 필요한 서비스입니다."); return; }
    postRating({ id: feedId, score: rating });
  };
  
  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    alert("URL이 클립보드에 복사되었습니다.");
  };
  const goBack = () => router.back();


  const renderContent = () => {
    if (isLoading) {
      return <div className="flex justify-center items-center h-[60vh]"><div className="animate-pulse text-gray-500">로딩 중...</div></div>;
    }
    if (isError || !feed) {
      return <div className="flex flex-col justify-center items-center h-[60vh] gap-4"><p className="text-gray-500">피드를 찾을 수 없습니다.</p><Button variant="outline" onClick={() => router.push('/')}>메인으로 돌아가기</Button></div>;
    }

    const isPressRelease = feed.category.name === "보도자료";
    
    return (
      // --- 👇 [수정] 이 부분이 새로운 레이아웃의 핵심입니다. ---
      <div className="max-w-3xl mx-auto relative">
        {/* --- 1. 추천 섹션 (Absolute Position) --- */}
        {/* 
          - `absolute`: 문서 흐름에서 벗어나 자유롭게 위치함
          - `right-full`: 오른쪽 끝을 부모의 왼쪽 끝(right: 100%)에 맞춤
          - `mr-8`: 본문과의 간격을 위한 오른쪽 여백
          - `w-72`: 추천 섹션의 너비를 고정
          - `hidden lg:block`: 모바일/태블릿에서는 숨기고, 데스크탑에서만 표시
        */}
        <aside className="absolute right-full mr-8 w-72 hidden lg:block">
          <div className="sticky top-24">
            <FeedRecommendations feedId={feed.id} isSourcePressRelease={isPressRelease} />
          </div>
        </aside>
        
        {/* --- 2. 피드 본문 섹션 (기존 중앙 정렬 유지) --- */}
        {/* 이 div는 이전과 동일하게 mx-auto 효과를 받아 중앙에 위치합니다. */}
        <div>
          <Button variant="ghost" onClick={goBack} className="mb-6 flex items-center gap-1"><ArrowLeft className="h-4 w-4" /><span>뒤로가기</span></Button>
          <h1 className="text-3xl font-bold mb-4 text-gray-900">{feed.title}</h1>
          <div className="flex flex-wrap items-center gap-3 mb-6 text-sm text-gray-500">
            <Badge variant="outline" className="bg-gray-100">{feed.organization.name}</Badge>
            <Badge variant="outline" className="bg-gray-50">{feed.category.name}</Badge>
            <span>조회수 {feed.view_count.toLocaleString()}</span>
            <span>•</span>
            <span>{formatDate(feed.published_date)}</span>
            <div className="flex items-center gap-1"><Star className="h-4 w-4 fill-yellow-400 text-yellow-400" /><span>{feed.average_rating.toFixed(1)}</span></div>
          </div>
          <div className="flex items-center gap-4 mb-8 pb-6 border-b border-gray-200">
            {/* ... (북마크, 공유, 별점 버튼은 동일) ... */}
            <Button variant="outline" className={`flex items-center gap-2 ${isBookmarked ? "text-yellow-500" : ""}`} onClick={handleToggleBookmark}><Bookmark className={`h-4 w-4 ${isBookmarked ? "fill-current" : ""}`} /><span>{isBookmarked ? "북마크됨" : "북마크"}</span></Button>
            <Button variant="outline" className="flex items-center gap-2" onClick={handleShare}><Share2 className="h-4 w-4" /><span>공유</span></Button>
            <div className="ml-auto flex items-center gap-1">
              <span className="text-sm text-gray-500 mr-2">별점 주기:</span>
              {[1, 2, 3, 4, 5].map((star) => (<Button key={star} variant="ghost" size="icon" className={`h-8 w-8 ${userRating >= star ? "text-yellow-400" : "text-gray-300"}`} onClick={() => handleRating(star)}><Star className={`h-5 w-5 ${userRating >= star ? "fill-current" : ""}`} /></Button>))}
            </div>
          </div>
          
          <div className="mb-8 pb-8 border-b border-gray-200">
            <h3 className="text-lg font-bold mb-4">원문 보기</h3>
            <PdfViewer fileUrl={feed.pdf_url} />
          </div>

          <div className="mb-8">
            <h3 className="text-lg font-medium mb-2">원문 링크</h3>
            <a href={feed.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{feed.source_url}</a>
          </div>
        </div>
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
      <ScrollToTopButton />
    </div>
  );
}