'use client';

import { motion } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation'; // [3단계 추가] 라우터 훅 임포트
import { MindMapNode } from './MindMapNode';
import { ZoomPanContainer } from './ZoomPanContainer';
import { Button } from '@/components/ui/button';
import { ArrowLeft, RotateCcw } from 'lucide-react';
import type { GraphNode, GraphEdge } from '@/lib/types/graph';

import { useExpandMutation } from '@/hooks/mutations/useGraphMutations';

interface MindMapDisplayNode extends GraphNode {
  x: number;
  y: number;
  level: number;
  parentId?: string;
  width: number;
  height: number;
}

interface MindMapProps {
  keyword: string;
  initialNodes: GraphNode[];
  initialEdges: GraphEdge[];
  onBack: () => void;
}

export function MindMap({ keyword, initialNodes, initialEdges, onBack }: MindMapProps) {
  const [allNodes, setAllNodes] = useState<GraphNode[]>(initialNodes);
  const [allEdges, setAllEdges] = useState<GraphEdge[]>(initialEdges);
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [nodes, setNodes] = useState<MindMapDisplayNode[]>([]);
  const [zoomPanKey, setZoomPanKey] = useState(0);

  const LEVEL_SPACING = 300;
  const NODE_SPACING = 60;
  const CENTER_X = 2200;
  const CENTER_Y = 1800;
  
  const getNodeCategoryByType = (type: GraphNode['type']): number => {
    switch (type) {
      case 'feed': return 0;
      case 'organization': return 1;
      case 'keyword': return 2;
      default: return 3;
    }
  };

  const expandMutation = useExpandMutation({
    onSuccess: (response, variables) => {
      if (response.success && response.data) {
        const nodeIds = new Set(allNodes.map(n => n.id));
        const newNodes = response.data.nodes.filter(n => !nodeIds.has(n.id));
        setAllNodes(prev => [...prev, ...newNodes]);

        const edgeIds = new Set(allEdges.map(e => e.id));
        const newEdges = response.data.edges.filter(e => !edgeIds.has(e.id));
        setAllEdges(prev => [...prev, ...newEdges]);
        
        setExpandedNodes(prev => new Set(prev).add(variables.nodeId));
      }
    },
    onError: (error) => {
      console.error("노드 확장 실패:", error);
    },
  });

  const calculateLayout = useCallback((
    baseNodes: GraphNode[],
    baseEdges: GraphEdge[],
    expandedSet: Set<string>
  ): MindMapDisplayNode[] => {
    
    const nodeMap = new Map<string, GraphNode>(baseNodes.map(n => [n.id, n]));
    const edgeMap = new Map<string, GraphEdge[]>();
    baseEdges.forEach(edge => {
      if (!edgeMap.has(edge.source)) edgeMap.set(edge.source, []);
      edgeMap.get(edge.source)!.push(edge);
    });

    const displayNodes: MindMapDisplayNode[] = [];
    const processedNodes = new Set<string>();

    const centerNodeData = baseNodes.find(n => n.id === `keyword_${keyword}`);
    if (!centerNodeData) return [];
    
    const queue: [MindMapDisplayNode | null, number][] = [[null, 0]]; // [parentNode, level]
    
    const centerNode: MindMapDisplayNode = {
      ...centerNodeData, x: CENTER_X, y: CENTER_Y, level: 0, width: 160, height: 50
    };
    displayNodes.push(centerNode);
    processedNodes.add(centerNode.id);

    const childrenOfCenter = edgeMap.get(centerNode.id) || [];
    childrenOfCenter.forEach(edge => queue.push([displayNodes[0], 0]));
    
    while(queue.length > 0) {
      const [parentNode, level] = queue.shift()!;
      if (!parentNode) continue;

      if (parentNode.level > 0 && !expandedSet.has(parentNode.id)) {
        continue;
      }

      const childrenEdges = edgeMap.get(parentNode.id) || [];
      const childNodeCount = childrenEdges.length;
      const startY = parentNode.y - (childNodeCount - 1) * NODE_SPACING / 2;

      childrenEdges.forEach((edge, index) => {
        const childNodeData = nodeMap.get(edge.target);
        if (childNodeData && !processedNodes.has(childNodeData.id)) {
          const childNode: MindMapDisplayNode = {
            ...childNodeData,
            x: parentNode.x + LEVEL_SPACING,
            y: startY + index * NODE_SPACING,
            level: level + 1,
            parentId: parentNode.id,
            width: Math.max(100, 140 - (level + 1) * 10),
            height: Math.max(32, 40 - (level + 1) * 2),
          };
          displayNodes.push(childNode);
          processedNodes.add(childNode.id);
          queue.push([childNode, level + 1]);
        }
      });
    }

    const adjustForCollisions = (nodesToAdjust: MindMapDisplayNode[]): MindMapDisplayNode[] => {
      const adjustedNodes = [...nodesToAdjust];      
      const nodesByLevel: { [level: number]: MindMapDisplayNode[] } = {};
      adjustedNodes.forEach(node => {
        if (!nodesByLevel[node.level]) nodesByLevel[node.level] = [];
        nodesByLevel[node.level].push(node);
      });
      const levels = Object.keys(nodesByLevel).map(Number).sort((a, b) => a - b);
      levels.forEach(level => {
        if (level === 0) return;
        const levelNodes = nodesByLevel[level];
        if (!levelNodes || levelNodes.length === 0) return;
        const nodesByParent: { [parentId: string]: MindMapDisplayNode[] } = {};
        levelNodes.forEach(node => {
          const parentId = node.parentId || 'center';
          if (!nodesByParent[parentId]) nodesByParent[parentId] = [];
          nodesByParent[parentId].push(node);
        });
        const parentIds = Object.keys(nodesByParent);
        parentIds.sort((a, b) => {
          const parentA = adjustedNodes.find(n => n.id === a);
          const parentB = adjustedNodes.find(n => n.id === b);
          return (parentA?.y || 0) - (parentB?.y || 0);
        });
        parentIds.forEach((parentId) => {
          const parentNode = adjustedNodes.find(n => n.id === parentId);
          const childNodes = nodesByParent[parentId];
          if (!parentNode || !childNodes || childNodes.length === 0) return;
          childNodes.sort((a, b) => a.y - b.y);
          const groupHeight = (childNodes.length - 1) * NODE_SPACING;
          let startY = parentNode.y - groupHeight / 2;
          childNodes.forEach((child, index) => {
            child.y = startY + index * NODE_SPACING;
          });
        });
        parentIds.forEach((parentId, groupIndex) => {
          if (groupIndex === 0) return;
          const currentGroup = nodesByParent[parentId];
          const previousParentId = parentIds[groupIndex - 1];
          const previousGroup = nodesByParent[previousParentId];
          if (!currentGroup || currentGroup.length === 0 || !previousGroup || previousGroup.length === 0) return;
          const currentMinY = Math.min(...currentGroup.map(n => n.y));
          const previousMaxY = Math.max(...previousGroup.map(n => n.y));
          const minRequiredGap = NODE_SPACING * 0.8;
          if (currentMinY - previousMaxY < minRequiredGap) {
            const adjustment = (previousMaxY + minRequiredGap) - currentMinY;
            currentGroup.forEach(node => {
              node.y += adjustment;
            });
            const parentNode = adjustedNodes.find(n => n.id === parentId);
            if (parentNode) {
              const groupCenterY = (Math.min(...currentGroup.map(n => n.y)) + Math.max(...currentGroup.map(n => n.y))) / 2;
              parentNode.y = groupCenterY;
            }
          }
        });
        const parentNodes = adjustedNodes.filter(n => parentIds.includes(n.id));
        parentNodes.sort((a, b) => a.y - b.y);
        for (let i = 1; i < parentNodes.length; i++) {
          const current = parentNodes[i];
          const previous = parentNodes[i - 1];
          const minDistance = NODE_SPACING * 0.6;
          if (current.y - previous.y < minDistance) {
            const adjustment = minDistance - (current.y - previous.y);
            current.y += adjustment;
            const childNodes = adjustedNodes.filter(n => n.parentId === current.id);
            childNodes.forEach(child => child.y += adjustment);
            for (let j = i + 1; j < parentNodes.length; j++) {
              parentNodes[j].y += adjustment;
              const laterChildNodes = adjustedNodes.filter(n => n.parentId === parentNodes[j].id);
              laterChildNodes.forEach(child => child.y += adjustment);
            }
          }
        }
      });
      return adjustedNodes;
    };
    
    return adjustForCollisions(displayNodes);

  }, [keyword, allNodes, allEdges, expandedNodes]);

  useEffect(() => {
    const calculatedNodes = calculateLayout(allNodes, allEdges, expandedNodes);
    setNodes(calculatedNodes);
  }, [allNodes, allEdges, expandedNodes, calculateLayout]);

  useEffect(() => {
    setAllNodes(initialNodes);
    setAllEdges(initialEdges);
    setExpandedNodes(new Set());
    setZoomPanKey(prev => prev + 1);
  }, [keyword, initialNodes, initialEdges]);

  const handleNodeClick = (nodeId: string) => {
    const nodeToExpand = allNodes.find(n => n.id === nodeId);
    if (!nodeToExpand) return;

    if (expandedNodes.has(nodeId)) {
      setExpandedNodes(prev => {
        const newSet = new Set(prev);
        newSet.delete(nodeId);
        return newSet;
      });
    } else {
      const hasChildrenInState = allEdges.some(edge => edge.source === nodeId);
      if (hasChildrenInState) {
        setExpandedNodes(prev => new Set(prev).add(nodeId));
      } else {
        expandMutation.mutate({
          nodeId: nodeToExpand.id,
          nodeType: nodeToExpand.type,
        });
      }
    }
  };

  const resetMap = () => {
    setExpandedNodes(new Set());
  };

  const createCurvedPath = (startX: number, startY: number, endX: number, endY: number) => {
    const controlX1 = startX + (endX - startX) * 0.6;
    const controlY1 = startY;
    const controlX2 = startX + (endX - startX) * 0.4;
    const controlY2 = endY;
    return `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;
  };

  const connections = allEdges.map(edge => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);

    if (!sourceNode || !targetNode) return null;
    
    const startX = sourceNode.x + sourceNode.width;
    const startY = sourceNode.y + sourceNode.height / 2;
    const endX = targetNode.x;
    const endY = targetNode.y + targetNode.height / 2;

    return (
      <motion.path
        key={edge.id}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 0.4 }}
        transition={{ duration: 0.5, delay: targetNode.level * 0.05 }}
        d={createCurvedPath(startX, startY, endX, endY)}
        stroke="#6366f1"
        strokeWidth="2"
        fill="none"
        className="pointer-events-none"
      />
    );
  }).filter(Boolean);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 relative">
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="absolute top-0 left-0 right-0 z-30 bg-white/95 backdrop-blur-md border-b border-gray-200/50 shadow-sm"
      >
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-6">
            <Button variant="outline" onClick={onBack} className="bg-white/80 hover:bg-white shadow-md">
              <ArrowLeft className="w-4 h-4 mr-2" />
              이전으로
            </Button>
            <div>
              {/* [3단계 수정] 헤더에 현재 키워드 표시 */}
              <h1 className="font-semibold text-gray-900 text-lg">{keyword}</h1>
              <p className="text-sm text-gray-500">마인드맵</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" onClick={resetMap} className="bg-white/80 hover:bg-white shadow-md">
              <RotateCcw className="w-4 h-4 mr-2" />
              모두 접기
            </Button>
            <div className="hidden md:block bg-blue-50 text-blue-700 px-3 py-2 rounded-lg border border-blue-200">
              <p className="text-sm">💡 노드의 확장/축소 버튼을 클릭하여 탐험하세요</p>
            </div>
          </div>
        </div>
      </motion.div>
      <ZoomPanContainer key={zoomPanKey} className="min-h-screen overflow-hidden pt-20">
        <div className="absolute z-0" style={{ width: '8000px', height: '6000px', left: '-2000px', top: '-1500px' }}>
          <svg className="absolute inset-0 pointer-events-none z-5" width="100%" height="100%">
            {connections}
          </svg>
          <div className="relative z-10 w-full h-full">
            {nodes.map(node => (
              <MindMapNode
                key={node.id}
                title={node.label}
                x={node.x}
                y={node.y}
                isCenter={node.level === 0}
                level={node.level}
                category={getNodeCategoryByType(node.type)}
                isExpanded={expandedNodes.has(node.id)}
                hasChildren={true}
                width={node.width}
                height={node.height}
                onClick={() => { // [3단계 추가] 노드 본체 클릭 이벤트 처리
                  if (node.type === 'feed') {
                    // 피드 상세 페이지로 이동
                    // [수정] 실제 feed의 ID를 사용하여 경로 생성 (예시)
                    window.open(`/feed/${node.id.replace('feed_', '')}`, '_blank');
                  } else if (node.type === 'organization') {
                    // 기관 상세 페이지로 이동
                    // [수정] 실제 organization의 이름을 사용하여 경로 생성 (예시)
                    window.open(`/organization/${node.label}`, '_blank');
                  }
                }}
                handleExpandClick={() => handleNodeClick(node.id)} // [3단계 추가] 확장 버튼 클릭 이벤트 처리
              />
            ))}
          </div>
        </div>
      </ZoomPanContainer>
    </div>
  );
}