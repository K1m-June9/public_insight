"use client";

import { useState } from 'react';
import { useRouter, useParams } from "next/navigation";
import dynamic from 'next/dynamic'; // 1. next/dynamic을 임포트
import { ArrowLeft, Bookmark, Scroll, Share2, Star, Building, Eye, Plus } from "lucide-react";
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
import KeywordSection from "@/components/feed/KeywordSection";
import DocumentSummary from "@/components/feed/DocumentSummary";

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

  const [isRatingDropdownOpen, setIsRatingDropdownOpen] = useState(false);

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
    const summaryParagraphs = feed.summary?.split('\n');
    
    return (
      // --- ▼ [수정] 이 부분부터 프로토타입에 맞춘 새로운 레이아웃으로 변경됩니다. ▼ ---
      <>
      
        {/* 1. Header Section */}
        <div className="border-b border-border bg-card">
          <div className="container px-4 py-6 md:px-6">
            <Button variant="ghost" size="sm" onClick={goBack} className="flex items-center space-x-2 mb-6">
              <ArrowLeft className="w-4 h-4" />
              <span>목록으로</span>
            </Button>
            
            
            <div className="space-y-4">
              <div className="flex items-center space-x-2">
                <Badge variant="default">{feed.category.name}</Badge>
                <Badge variant="secondary">{feed.organization.name}</Badge>
              </div>
              <h1 className="text-2xl leading-tight text-foreground">{feed.title}</h1>
              <div className="flex flex-wrap items-center justify-between gap-y-3">
                <div className="flex items-center flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                  <div className="flex items-center space-x-1">
                    <Building className="w-4 h-4" />
                    <span>{feed.organization.name}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Star className="w-4 h-4 text-yellow-400 fill-current" />
                    <span>{feed.average_rating.toFixed(1)}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Eye className="w-4 h-4" />
                    <span>{feed.view_count.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Bookmark className="w-4 h-4" />
                    {/* << [수정] API에서 받아온 bookmark_count를 사용함. */}
                    <span>{feed.bookmark_count.toLocaleString()}</span>
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <Button variant="ghost" size="sm" className={`flex items-center space-x-1 text-sm text-muted-foreground hover:text-primary ${isBookmarked ? "text-yellow-500 border-yellow-500" : ""}`} onClick={handleToggleBookmark}>
                    <Bookmark className={`w-4 h-4 ${isBookmarked ? "fill-current" : ""}`} />
                    <span>{isBookmarked ? "북마크됨" : "북마크"}</span>
                  </Button>
                  
                  {/* --- ▼ [수정] 이 부분이 새로운 별점 드롭다운 UI입니다. ▼ --- */}
                  <div className="relative">
                    <Button
                      variant="ghost"
                      size="sm"
                      className={`flex items-center space-x-1 text-sm text-muted-foreground hover:text-primary ${userRating > 0 ? "text-yellow-500 border-yellow-500" : ""}`}
                      onClick={() => setIsRatingDropdownOpen(prev => !prev)}
                    >
                      <Plus className="w-4 h-4" />
                      <span>{userRating > 0 ? `내 별점: ${userRating}점` : "별점 주기"}</span>
                    </Button>

                    {isRatingDropdownOpen && (
                      <div className="absolute top-full right-0 mt-2 w-48 bg-card border border-border rounded-lg shadow-lg p-2 z-50">
                        <div className="space-y-1">
                          <p className="text-xs text-muted-foreground px-2 pb-1">별점을 선택하세요</p>
                          {[5, 4, 3, 2, 1].map((rating) => (
                            <button
                              key={rating}
                              className={`flex items-center justify-between w-full p-2 text-sm rounded-md hover:bg-muted text-left ${userRating === rating ? "bg-muted font-semibold" : ""}`}
                              onClick={() => {
                                handleRating(rating);
                                setIsRatingDropdownOpen(false); // 별점 선택 후 드롭다운을 닫음.
                              }}
                            >
                              <span className={`${userRating === rating ? "text-yellow-500" : ""}`}>{rating}점</span>
                              <div className="flex items-center">
                                {Array.from({ length: 5 }).map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`h-4 w-4 ${i < rating ? "text-yellow-400 fill-current" : "text-muted-foreground/50"}`}
                                  />
                                ))}
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                    <Button variant="ghost" size="sm" className="flex items-center space-x-1 text-sm text-muted-foreground hover:text-primary" onClick={handleShare}>
                    <Share2 className="w-4 h-4" />
                    <span>공유</span>
                  </Button>
                  
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Summary Section */}
        {/* << [추가] DocumentSummary 컴포넌트를 렌더링하고, 변환된 요약문 데이터를 prop으로 전달함. */}
        <div className="bg-muted/30">
          <div className="container px-4 py-6 md:px-6">
            <DocumentSummary summaryText={summaryParagraphs} />
          </div>
        </div>

        {/* 3. Main Content Section */}
        <div className="container px-4 py-8 md:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-[288px_minmax(0,1fr)_288px] lg:gap-8 xl:gap-12">
            
            {/* Left Sidebar - Feed Recommendations */}
            <aside className="hidden lg:block">
              <div className="sticky top-24">
                {/* 기존 컴포넌트를 그대로 재사용함. */}
                <FeedRecommendations feedId={feed.id} isSourcePressRelease={isPressRelease} />
              </div>
            </aside>
            
            {/* PDF Viewer */}
            <div className="min-w-0">
               {/* 기존 PdfViewer 컴포넌트를 그대로 재사용하고, API에서 받은 pdf_url을 전달함. */}
              <PdfViewer fileUrl={feed.pdf_url} />
              <div className="mt-8 pt-6 border-t">
                  <h3 className="text-lg font-medium mb-2">원문 링크</h3>
                  <a href={feed.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline break-all">{feed.source_url}</a>
              </div>
            </div>

            {/* Right Sidebar - Related Keywords */}
            <aside className="hidden lg:block">
              <div className="sticky top-24">
                 {/* 기존 KeywordSection 컴포넌트를 그대로 재사용함. */}
                <KeywordSection feedId={feed.id} />
              </div>
            </aside>
          </div>
        </div>
      </>
      // --- ▲ [수정] 여기까지 새로운 레이아웃입니다. ▲ ---
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
          {renderContent()}
      </main>
      <Footer />
      <ScrollToTopButton />
    </div>
  );
}