"use client";

import { useState, useRef, useCallback } from 'react';
import { GraphNode, GraphEdge } from '@/lib/types/graph';
import { MindMapNode } from './MindMapNode';
import { motion, AnimatePresence } from 'framer-motion';

// ====================================================================
// Props 정의
// ====================================================================

interface MindMapCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  isExpanded: (nodeId: string) => boolean;
  onExpand: (nodeId: string, nodeType: string) => void;
}

// ====================================================================
// 헬퍼 함수
// ====================================================================

/**
 * 두 노드 사이에 부드러운 곡선 경로(SVG path data)를 생성합니다.
 */
const generateCurvePath = (fromNode: GraphNode, toNode: GraphNode): string => {
  // 노드의 우측 중앙에서 시작하여, 좌측 중앙으로 연결
  const fromX = (fromNode.metadata?.x || 0) + 140; // 노드 너비의 절반
  const fromY = fromNode.metadata?.y || 0;
  const toX = (toNode.metadata?.x || 0) - 140; // 노드 너비의 절반
  const toY = toNode.metadata?.y || 0;

  const midX = (fromX + toX) / 2;
  // 제어점을 조절하여 곡선의 부드러움을 결정
  const controlX1 = fromX + (midX - fromX) * 0.8;
  const controlX2 = toX - (toX - midX) * 0.8;
  
  return `M ${fromX} ${fromY} C ${controlX1} ${fromY}, ${controlX2} ${toY}, ${toX} ${toY}`;
};


// ====================================================================
// 메인 컴포넌트
// ====================================================================

export function MindMapCanvas({ nodes, edges, isExpanded, onExpand }: MindMapCanvasProps) {
  const [viewBox, setViewBox] = useState({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  // --- 이벤트 핸들러 ---

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    // 캔버스 배경을 클릭했을 때만 드래그 시작
    if (e.target === e.currentTarget) {
      setIsDragging(true);
      setDragStart({ x: e.clientX, y: e.clientY });
    }
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    
    // 마우스 이동량에 따라 viewBox의 x, y 좌표를 이동
    const deltaX = (e.clientX - dragStart.x) / viewBox.scale;
    const deltaY = (e.clientY - dragStart.y) / viewBox.scale;
    
    setViewBox(prev => ({ ...prev, x: prev.x - deltaX, y: prev.y - deltaY }));
    setDragStart({ x: e.clientX, y: e.clientY });
  }, [isDragging, dragStart, viewBox.scale]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const containerRect = containerRef.current?.getBoundingClientRect();
    if (!containerRect) return;

    const zoomFactor = e.deltaY > 0 ? 1.1 : 0.9; // 휠 방향에 따른 줌 배율
    const newScale = Math.max(0.2, Math.min(3, viewBox.scale * zoomFactor)); // 줌 범위 제한

    // 마우스 포인터를 중심으로 줌 인/아웃
    const mouseX = e.clientX - containerRect.left;
    const mouseY = e.clientY - containerRect.top;
    const worldX = viewBox.x + mouseX / viewBox.scale;
    const worldY = viewBox.y + mouseY / viewBox.scale;
    
    setViewBox({
      scale: newScale,
      x: worldX - mouseX / newScale,
      y: worldY - mouseY / newScale,
    });
  }, [viewBox]);

  // --- 렌더링 ---
  
  // 캔버스의 현재 보이는 영역을 계산
  const canvasWidth = (containerRef.current?.clientWidth || 1200) / viewBox.scale;
  const canvasHeight = (containerRef.current?.clientHeight || 800) / viewBox.scale;
  
  // 노드와 엣지를 렌더링하기 위한 데이터 맵 (빠른 조회를 위함)
  const nodeMap = new Map(nodes.map(node => [node.id, node]));

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full bg-muted/30 overflow-hidden cursor-grab active:cursor-grabbing"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // 캔버스 밖으로 나가도 드래그 중지
      onWheel={handleWheel}
    >
      <div className="relative w-full h-full">
        {/* Nodes */}
        <AnimatePresence>
          {nodes.map((node) => (
            <MindMapNode
              key={node.id}
              node={node}
              isExpanded={isExpanded(node.id)}
              onExpand={onExpand}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Edges (SVG) */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none"
        // 뷰박스를 제거하고, CSS transform으로 줌/패닝을 제어하도록 변경
      >
        <motion.g // 👈 g 태그를 motion.g로 변경하여 줌/패닝 애니메이션 적용
          animate={{
            scale: viewBox.scale,
            x: -viewBox.x * viewBox.scale,
            y: -viewBox.y * viewBox.scale,
          }}
          transition={{ duration: 0.5, ease: "circOut" }}
        >
          <AnimatePresence>
            {edges.map((edge) => {
              const fromNode = nodeMap.get(edge.source);
              const toNode = nodeMap.get(edge.target);

              if (!fromNode || !toNode) return null;

              // 🔧 [수정] path를 motion.path로 변경하여 나타나고 사라질 때 애니메이션 적용
              return (
                <motion.path
                  key={edge.id}
                  d={generateCurvePath(fromNode, toNode)}
                  stroke="hsl(var(--border))"
                  strokeWidth="2"
                  fill="none"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5 }}
                />
              );
            })}
          </AnimatePresence>
        </motion.g>
      </svg>
    </div>
  );
}