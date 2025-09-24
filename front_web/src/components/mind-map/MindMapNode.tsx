"use client";

import { memo } from "react";
import Link from "next/link";
import { ChevronRight, Eye, Star, Bookmark, Building, FileText, Tag, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GraphNode } from "@/lib/types/graph";
import { motion } from 'framer-motion';

// ====================================================================
// 헬퍼 함수 (컴포넌트 외부)
// ====================================================================

/**
 * 노드 타입에 따라 적절한 색상(CSS 변수)을 반환합니다.
 */
const getNodeColor = (type: string): string => {
  switch (type) {
    case 'feed': return 'hsl(var(--chart-1))';
    case 'organization': return 'hsl(var(--chart-2))';
    case 'user': return 'hsl(var(--chart-3))';
    case 'keyword': return 'hsl(var(--chart-4))';
    default: return 'hsl(var(--muted-foreground))';
  }
};

/**
 * 노드 타입에 따라 적절한 Lucide 아이콘 컴포넌트를 반환합니다.
 */
const getNodeIcon = (type: string) => {
  switch (type) {
    case 'feed': return FileText;
    case 'organization': return Building;
    case 'user': return Users;
    case 'keyword': return Tag;
    default: return Tag;
  }
};

// ====================================================================
// Props 정의
// ====================================================================

interface MindMapNodeProps {
  node: GraphNode;
  isExpanded: boolean;
  onExpand: (nodeId: string, nodeType: string) => void;
}

// ====================================================================
// 메인 컴포넌트
// ====================================================================

export const MindMapNode = memo(({ node, isExpanded, onExpand }: MindMapNodeProps) => {
  const IconComponent = getNodeIcon(node.type);
  const canExpand = !isExpanded;
  
  // 노드 타입과 ID를 기반으로 페이지 이동 여부 및 경로 결정
  const isFeed = node.type === 'feed';
  const isOrganization = node.type === 'organization';
  const entityId = node.id.split('_')[1]; // 예: "feed_123" -> "123"

  const NodeContent = (
    <motion.div
      // layout 속성은 위치(left, top)가 변경될 때 자동으로 부드러운 애니메이션을 적용해 줌
      layout="position" 
      // 초기, 애니메이션, 종료 상태 정의
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      // 이제 위치 스타일은 animate 속성에서 제어하지 않고, style에 직접 적용
      style={{
        // elkjs가 계산해준 x, y 좌표를 사용
        left: `${node.metadata?.x || 0}px`,
        top: `${node.metadata?.y || 0}px`,
        // 노드 너비/높이의 절반만큼 이동하여 중앙 정렬
        transform: 'translate(-50%, -50%)',
        // borderColor는 이전과 동일
        borderColor: getNodeColor(node.type),
      }}
      className="absolute p-4 rounded-lg border-2 shadow-lg bg-card w-[280px] cursor-pointer hover:shadow-xl hover:scale-105"
    >
      {/* 1. Node Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <IconComponent
            className="w-4 h-4 flex-shrink-0"
            style={{ color: getNodeColor(node.type) }}
          />
          <span className="text-sm font-medium leading-tight truncate">{node.label}</span>
        </div>
        
        {/* Expand Button */}
        {canExpand && (
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 hover:bg-muted"
            onClick={(e) => {
              e.stopPropagation(); // Link 이동 방지
              onExpand(node.id, node.type);
            }}
            title="확장"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* 2. Feed Metadata (피드 타입일 경우에만 렌더링) */}
      {isFeed && node.metadata && (
        <div className="mt-3 pt-3 border-t border-border">
          <div className="grid grid-cols-3 gap-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Eye className="w-3 h-3" />
              <span>{node.metadata.view_count?.toLocaleString() || 0}</span>
            </div>
            <div className="flex items-center gap-1">
              <Star className="w-3 h-3" />
              <span>{node.metadata.avg_rating?.toFixed(1) || '0.0'}</span>
            </div>
            <div className="flex items-center gap-1">
              <Bookmark className="w-3 h-3" />
              <span>{node.metadata.bookmark_count || 0}</span>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );

  // 3. 노드 타입에 따라 조건부로 Link 컴포넌트로 감싸줌
  if (node.type === 'feed') {
    // legacyBehavior와 passHref를 제거하고, NodeContent를 직접 자식으로 넣음
    return (
      <Link href={`/feed/${entityId}`}>
        {NodeContent}
      </Link>
    );
  }
  
  if (node.type === 'organization') {
    // legacyBehavior와 passHref를 제거
    return (
      <Link href={`/organization/${encodeURIComponent(node.label)}`}>
        {NodeContent}
      </Link>
    );
  }

  // 링크가 없는 다른 모든 노드 타입
  return NodeContent;
});

// React 개발자 도구에서 디버깅을 용이하게 하기 위한 설정
MindMapNode.displayName = "MindMapNode";