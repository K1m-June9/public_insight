'use client';

import { useState } from 'react';
import { MainPage } from '@/components/mind-map/MainPage';
import { MindMap } from '@/components/mind-map/MindMap';

// 참고: 컴포넌트 경로인 '@/components/...'는 
// 프로젝트의 경로 별칭(alias) 설정에 따라 다를 수 있습니다.
// 만약 './components/...' 또는 '../../components/...' 등 상대 경로를 사용한다면
// 그에 맞게 수정해주세요.

export default function ExplorePage() {
  // 현재 선택된 주제를 관리하는 상태
  // 값이 null이면 메인 페이지, 값이 있으면 마인드맵 페이지를 보여줍니다.
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);

  /**
   * MainPage에서 주제 카드를 클릭했을 때 호출되는 함수입니다.
   * 선택된 주제로 상태를 업데이트하여 마인드맵을 표시합니다.
   * @param topic - 선택된 주제 문자열
   */
  const handleWordSelect = (topic: string) => {
    setSelectedTopic(topic);
  };

  /**
   * MindMap에서 '메인으로' 버튼을 클릭했을 때 호출되는 함수입니다.
   * 선택된 주제 상태를 null로 만들어 다시 메인 페이지를 보여줍니다.
   */
  const handleBack = () => {
    setSelectedTopic(null);
  };

  return (
    <main>
      {selectedTopic ? (
        // 선택된 주제가 있으면 MindMap 컴포넌트를 렌더링합니다.
        <MindMap 
          centerTopic={selectedTopic} 
          onBack={handleBack} 
        />
      ) : (
        // 선택된 주제가 없으면 MainPage 컴포넌트를 렌더링합니다.
        <MainPage 
          onWordSelect={handleWordSelect} 
        />
      )}
    </main>
  );
}