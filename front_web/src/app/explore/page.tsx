"use client";

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useExploreQuery } from '@/hooks/queries/useGraphQueries';
import { useExpandMutation } from '@/hooks/mutations/useGraphMutations';
import { GraphNode, GraphEdge, GraphResponse } from '@/lib/types/graph';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Loader2, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

import ReactFlow, {
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { MindMapNode } from '@/components/mind-map/MindMapNode';

import ELK from 'elkjs/lib/elk.bundled.js';

const elk = new ELK();

// 1. [핵심] nodeTypes 정의를 컴포넌트 밖으로 이동시킴.
// 이렇게 하면 컴포넌트가 재렌더링될 때마다 새로운 객체가 생성되는 것을 방지함.
const nodeTypes = { mindmapNode: MindMapNode };

const getLayoutedElements = async (nodes: GraphNode[], edges: GraphEdge[]) => {
  if (nodes.length === 0) {
    return [];
  }

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

  try {
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
  } catch (e) {
    console.error("ELK layout error:", e);
    return nodes.map(node => ({ ...node, metadata: { ...node.metadata, x: 0, y: 0 } }));
  }
};

function ExplorePageContent() {
  const searchParams = useSearchParams();
  const initialKeyword = searchParams.get('keyword');

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  const {
    data: exploreResponse,
    isLoading: isExploreLoading,
    isError: isError
  } = useExploreQuery(initialKeyword || '', {
    enabled: !!initialKeyword,
  });

  const {
    mutate: expandNode,
    isPending: isExpandPending
  } = useExpandMutation({
    onSuccess: (response: GraphResponse) => {
      if (response.data) {
        const existingNodes: GraphNode[] = nodes.map(n => n.data.node);
        const existingEdges: GraphEdge[] = edges.map(e => ({ 
            id: e.id, 
            source: e.source, 
            target: e.target, 
            label: e.label ? String(e.label) : null 
        }));

        const newGraphNodes = [...existingNodes, ...response.data.nodes];
        const newGraphEdges = [...existingEdges, ...response.data.edges];
        
        getLayoutedElements(newGraphNodes, newGraphEdges).then(layoutedNodes => {
            setNodes(layoutedNodes.map(node => convertToReactFlowNode(node)));
            setEdges(newGraphEdges.map(edge => convertToReactFlowEdge(edge)));
        });
      }
    },
    onError: (error) => {
      console.error("Expansion failed:", error);
    }
  });

  const convertToReactFlowNode = (node: GraphNode): Node => ({
    id: node.id,
    type: 'mindmapNode',
    position: { x: node.metadata?.x || 0, y: node.metadata?.y || 0 },
    data: { node },
  });

  const convertToReactFlowEdge = (edge: GraphEdge): Edge => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.label,
    type: 'smoothstep',
    animated: true,
  });

  useEffect(() => {
    if (exploreResponse?.data) {
      const { nodes: apiNodes, edges: apiEdges } = exploreResponse.data;
      if (apiNodes && apiNodes.length > 0) {
        getLayoutedElements(apiNodes, apiEdges)
          .then(layoutedNodes => {
            setNodes(layoutedNodes.map(node => convertToReactFlowNode(node)));
            setEdges(apiEdges.map(edge => convertToReactFlowEdge(edge)));
          });
      }
    }
  }, [exploreResponse]);

  const handleExpand = useCallback((nodeId: string, nodeType: string) => {
    if (expandedNodes.has(nodeId) || isExpandPending) return;
    setExpandedNodes(prev => new Set(prev).add(nodeId));
    expandNode({ nodeId, nodeType });
  }, [expandedNodes, isExpandPending, expandNode]);
  
  const nodesWithProps = nodes.map(node => {
    return {
      ...node,
      data: {
        ...node.data,
        isExpanded: expandedNodes.has(node.id),
        onExpand: handleExpand,
      }
    };
  });

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
    return (
        <div className="flex flex-grow items-center justify-center">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <p className="ml-4 text-lg">"{initialKeyword}"에 대한 지식 그래프를 불러오는 중...</p>
        </div>
    );
  }

  if (isError) {
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
          {isExpandPending && <Loader2 className="w-5 h-5 animate-spin text-muted-foreground ml-auto" />}
        </div>
      </div>
      
      <div className="flex-grow relative">
        <ReactFlow
          nodes={nodesWithProps}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          className="bg-muted/30"
        >
          <Controls />
          <Background />
        </ReactFlow>
      </div>
    </div>
  );
}

export default function ExplorePage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <div className="flex flex-col h-screen">
                <Header />
                <main className="flex-grow flex flex-col">
                    <ExplorePageContent />
                </main>
                <Footer />
            </div>
        </Suspense>
    );
}