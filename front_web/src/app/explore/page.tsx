"use client";

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useExploreQuery } from '@/hooks/queries/useGraphQueries';
import { useExpandMutation } from '@/hooks/mutations/useGraphMutations';
import { GraphNode, GraphEdge, GraphResponse } from '@/lib/types/graph';
import { MindMapCanvas } from '@/components/mind-map/MindMapCanvas';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

// 🔧 1. elkjs를 임포트합니다.
import ELK from 'elkjs/lib/elk.bundled.js';

// 🔧 2. ELK 인스턴스는 컴포넌트 외부에서 한 번만 생성하여 재사용합니다. (성능 최적화)
const elk = new ELK();

// 🔧 3. elkjs를 사용하여 레이아웃을 계산하는 새로운 헬퍼 함수를 정의합니다.
const getLayoutedElements = async (nodes: GraphNode[], edges: GraphEdge[]) => {
  const graph = {
    id: 'root',
    layoutOptions: { 
      'elk.algorithm': 'mrtree',
      'elk.direction': 'RIGHT',
      'elk.spacing.nodeNode': '50',
      'elk.layered.spacing.nodeNodeBetweenLayers': '250',
      'elk.mrtree.searchOrder.mode': 'BFS',
    },
    children: nodes.map(node => ({ id: node.id, width: 280, height: 110 })),
    edges: edges.map(edge => ({ id: edge.id, sources: [edge.source], targets: [edge.target] })),
  };

  // 🔧 [수정] 중복된 라인 제거
  const layoutedGraph = await elk.layout(graph);
  
  return nodes.map(node => {
    const layoutedNode = layoutedGraph.children?.find(n => n.id === node.id);
    return {
      ...node,
      metadata: {
        ...node.metadata,
        x: layoutedNode?.x || 0,
        y: layoutedNode?.y || 0,
      }
    };
  });
};


function ExplorePageContent() {
  const searchParams = useSearchParams();
  const initialKeyword = searchParams.get('keyword');

  // --- 상태 관리 (변경 없음) ---
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  
  // --- 데이터 페칭 ---

  // 초기 데이터 로딩 (변경 없음)
  const { 
    data: exploreResponse, 
    isLoading: isExploreLoading, 
    isError: isExploreError 
  } = useExploreQuery(initialKeyword || '', {
    enabled: !!initialKeyword,
  });

  // 노드 확장 로딩 (onSuccess 로직 수정)
  const { 
    mutate: expandNode, 
    isPending: isExpandPending 
  } = useExpandMutation({
    onSuccess: (response: GraphResponse) => {
      if (response.data) {
        // 🔧 4. 확장 성공 시, 새로운 노드/엣지를 포함하여 전체 레이아웃을 다시 계산합니다.
        const newNodes = [...nodes, ...response.data.nodes];
        const newEdges = [...edges, ...response.data.edges];
        
        getLayoutedElements(newNodes, newEdges).then(layoutedNodes => {
          setNodes(layoutedNodes); // 좌표가 업데이트된 전체 노드 리스트로 상태를 업데이트
          setEdges(newEdges);     // 엣지 리스트도 업데이트
        });
      }
    },
    onError: (error) => {
      console.error("Expansion failed:", error);
    }
  });

  // --- 효과 ---

  // 🔧 5. 초기 데이터 로딩 성공 시, elkjs를 통해 레이아웃을 계산하고 상태를 업데이트합니다.
  useEffect(() => {
    if (exploreResponse?.data) {
      // API로부터 받은 좌표 없는 노드/엣지를 레이아웃 함수에 전달
      getLayoutedElements(exploreResponse.data.nodes, exploreResponse.data.edges)
        .then(layoutedNodes => {
          // elkjs가 계산한 좌표가 포함된 노드 리스트로 상태 설정
          setNodes(layoutedNodes);
          setEdges(exploreResponse.data.edges);
        });
    }
  }, [exploreResponse]);

  // --- 이벤트 핸들러 ---

  const handleExpand = (nodeId: string, nodeType: string) => {
    // 이미 확장된 노드는 다시 요청하지 않음
    if (expandedNodes.has(nodeId)) return;
    
    setExpandedNodes(prev => new Set(prev).add(nodeId));
    expandNode({ nodeId, nodeType });
  };
  
  const isExpanded = (nodeId: string) => expandedNodes.has(nodeId);

  // --- 렌더링 로직 ---

  if (!initialKeyword) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <AlertTriangle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-xl font-semibold">잘못된 접근입니다.</h2>
        <p className="text-muted-foreground mt-2">탐색할 키워드가 지정되지 않았습니다.</p>
        <Button asChild className="mt-6">
          <Link href="/">메인으로 돌아가기</Link>
        </Button>
      </div>
    );
  }

  if (isExploreLoading) {
    // 🔧 [수정] 로딩/에러 화면도 전체 높이를 차지하도록 수정
    return (
      <div className="flex flex-grow items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
        <p className="ml-4 text-lg">"{initialKeyword}"에 대한 지식 그래프를 불러오는 중...</p>
      </div>
    );
  }

  if (isExploreError) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <AlertTriangle className="w-12 h-12 text-destructive mb-4" />
        <h2 className="text-xl font-semibold">오류 발생</h2>
        <p className="text-muted-foreground mt-2">데이터를 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.</p>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* 1. 헤더 영역 */}
      <div className="border-b border-border bg-card p-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <Button variant="ghost" asChild>
            <Link href="/">
              <ArrowLeft className="w-4 h-4 mr-2" />
              메인으로
            </Link>
          </Button>
          <h1 className="text-lg font-semibold">
            탐색 주제: <span className="text-primary">{initialKeyword}</span>
          </h1>
          {/* TODO: 여기에 줌/패닝 컨트롤 버튼 추가 */}
          {isExpandPending && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground ml-auto" />}
        </div>
      </div>
      
      {/* 2. 메인 캔버스 영역 */}
      <div className="flex-grow relative">
        <MindMapCanvas
          nodes={nodes}
          edges={edges}
          isExpanded={isExpanded}
          onExpand={handleExpand}
        />
      </div>
    </div>
  );
}


// Suspense 바운더리 적용
export default function ExplorePage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            {/* 🔧 [핵심 수정] 페이지 전체 레이아웃을 flexbox로 변경 */}
            <div className="flex flex-col h-screen"> {/* 👈 h-screen 추가 */}
                <Header />
                {/* 🔧 [수정] main 태그가 남은 공간을 모두 채우도록 flex-grow 추가 */}
                <main className="flex-grow flex flex-col"> {/* 👈 flex와 flex-col 추가 */}
                    <ExplorePageContent />
                </main>
                <Footer />
            </div>
        </Suspense>
    );
}