'use client';

import { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useRouter } from 'next/navigation'; // [추가] 뒤로가기 버튼을 위해 import

// [수정] 데이터 로딩을 위한 커스텀 훅 임포트
import { useExploreQuery } from '@/hooks/queries/useGraphQueries';

// [수정] 실제 데이터와 연동될 MindMap 컴포넌트 임포트
import { MindMap } from '@/components/mind-map/MindMap';
import { Button } from '@/components/ui/button'; // [추가] 에러 화면에서 사용

/**
 * useSearchParams 훅을 사용하고 실제 컨텐츠를 렌더링하는 내부 컴포넌트
 */
function ExplorePageContent() {
  const searchParams = useSearchParams();
  const router = useRouter(); // [추가] 뒤로가기 함수 사용
  const keyword = searchParams.get('keyword');

  // URL에 keyword가 없으면 안내 메시지를 표시
  if (!keyword) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50">
        <h1 className="text-2xl font-semibold text-slate-700 mb-4">탐색할 키워드가 필요합니다.</h1>
        <p className="text-slate-500">인기 키워드 목록 등에서 키워드를 선택하여 탐색을 시작해주세요.</p>
        <Button onClick={() => router.back()} className="mt-6">이전 페이지로 돌아가기</Button>
      </div>
    );
  }

  // [추가] useExploreQuery를 사용하여 키워드로 초기 마인드맵 데이터를 가져옴
  const { data: response, isLoading, isError, error } = useExploreQuery(keyword);

  // 로딩 상태 UI
  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">로딩 중...</div>;
  }

  // 에러 상태 UI
  if (isError || !response?.success) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-red-50">
        <h1 className="text-2xl font-semibold text-red-700 mb-4">데이터를 불러올 수 없습니다.</h1>
        <p className="text-red-500">
          오류: {error?.message || '알 수 없는 오류가 발생했습니다.'}
        </p>
        <Button variant="destructive" onClick={() => router.back()} className="mt-6">
          이전 페이지로 돌아가기
        </Button>
      </div>
    );
  }

  // [수정] 데이터 로딩 성공 시, MindMap 컴포넌트에 keyword와 API 데이터를 props로 전달
  return (
    <MindMap
      keyword={keyword}
      initialNodes={response.data?.nodes || []}
      initialEdges={response.data?.edges || []}
      onBack={() => router.back()} // [추가] 뒤로가기 기능 연결
    />
  );
}


/**
 * Suspense로 Content를 감싸는 메인 페이지 컴포넌트
 */
export default function ExplorePage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">로딩 중...</div>}>
      <ExplorePageContent />
    </Suspense>
  );
}