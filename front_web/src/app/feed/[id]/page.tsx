// 파일 위치: app/feed/[id]/page.tsx

"use client";

import { useRouter, useParams } from "next/navigation";
import { ArrowLeft, Bookmark, Share2, Star } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useFeedDetailQuery } from "@/hooks/queries/useFeedQueries";
import { useToggleBookmarkMutation, usePostRatingMutation } from "@/hooks/mutations/useFeedMutations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/date";

export default function FeedDetailPage() {
  const router = useRouter();
  const params = useParams();
  const feedId = Number(params.id);

  const { user } = useAuth(); // 로그인 상태 확인용

  // 1. 데이터 페칭
  const { data: feedData, isLoading, isError } = useFeedDetailQuery(feedId, {
    enabled: !isNaN(feedId) && feedId > 0,
  });
  
  // 2. 뮤테이션 훅 사용
  const { mutate: toggleBookmark } = useToggleBookmarkMutation();
  const { mutate: postRating } = usePostRatingMutation();

  const feed = feedData?.data.feed;
  
  // 3. 북마크 및 별점 상태는 API 응답에서 직접 가져옵니다. (향후 API 수정 필요)
  // 현재는 API 응답에 이 정보가 없으므로, 임시로 false와 0을 사용합니다.
  // TODO: 백엔드 API 응답(`FeedDetail`)에 is_bookmarked: boolean, user_rating: number 필드 추가 필요
  const isBookmarked = feed?.is_bookmarked ?? false;
  const userRating = feed?.user_rating ?? 0;

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

  if (isLoading) {
    return (
      <div className="container px-4 py-8 md:px-6">
        <div className="flex justify-center items-center h-[60vh]">
          <div className="animate-pulse text-gray-500">로딩 중...</div>
        </div>
      </div>
    );
  }

  if (isError || !feed) {
    return (
      <div className="container px-4 py-8 md:px-6">
        <div className="flex flex-col justify-center items-center h-[60vh] gap-4">
          <p className="text-gray-500">피드를 찾을 수 없습니다.</p>
          <Button variant="outline" onClick={() => router.push('/')}>메인으로 돌아가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8 md:px-6">
      <div className="max-w-3xl mx-auto">
        <Button variant="ghost" onClick={goBack} className="mb-6 flex items-center gap-1"><ArrowLeft className="h-4 w-4" /><span>뒤로가기</span></Button>
        <h1 className="text-3xl font-bold mb-4 text-gray-900">{feed.title}</h1>
        <div className="flex flex-wrap items-center gap-3 mb-6 text-sm text-gray-500">
          <Badge variant="outline" className="bg-gray-100">{feed.organization.name}</Badge>
          <Badge variant="outline" className="bg-gray-50">{feed.category.name}</Badge>
          <div className="flex items-center gap-1"><span>조회수 {feed.view_count.toLocaleString()}</span></div>
          <div>작성일 {formatDate(feed.published_date)}</div>
          <div className="flex items-center gap-1"><Star className="h-4 w-4 fill-yellow-400 text-yellow-400" /><span>{feed.average_rating.toFixed(1)}</span></div>
        </div>
        <div className="flex items-center gap-4 mb-8 pb-6 border-b border-gray-200">
          <Button variant="outline" className={`flex items-center gap-2 ${isBookmarked ? "text-yellow-500" : ""}`} onClick={handleToggleBookmark}>
            <Bookmark className={`h-4 w-4 ${isBookmarked ? "fill-current" : ""}`} /><span>{isBookmarked ? "북마크됨" : "북마크"}</span>
          </Button>
          <Button variant="outline" className="flex items-center gap-2" onClick={handleShare}><Share2 className="h-4 w-4" /><span>공유</span></Button>
          <div className="ml-auto flex items-center gap-1">
            <span className="text-sm text-gray-500 mr-2">별점 주기:</span>
            {[1, 2, 3, 4, 5].map((star) => (
              <Button key={star} variant="ghost" size="icon" className={`h-8 w-8 ${userRating >= star ? "text-yellow-400" : "text-gray-300"}`} onClick={() => handleRating(star)}>
                <Star className={`h-5 w-5 ${userRating >= star ? "fill-current" : ""}`} />
              </Button>
            ))}
          </div>
        </div>
        <div className="prose max-w-none mb-8 pb-8 border-b border-gray-200" dangerouslySetInnerHTML={{ __html: feed.content }} />
        <div className="mb-8">
          <h3 className="text-lg font-medium mb-2">원문 링크</h3>
          <a href={feed.source_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">{feed.source_url}</a>
        </div>
      </div>
    </div>
  );
}