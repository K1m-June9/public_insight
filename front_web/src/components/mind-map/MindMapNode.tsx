"use client";

import { memo } from "react";
import Link from "next/link";
// 1. [핵심] reactflow에서 Handle과 Position을 임포트함.
import { Handle, Position } from 'reactflow';
import { ChevronRight, Eye, Star, Bookmark, Building, FileText, Tag, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { GraphNode } from "@/lib/types/graph";
import { motion } from 'framer-motion';

const getNodeColor = (type: string): string => {
  switch (type) {
    case 'feed': return 'hsl(var(--chart-1))';
    case 'organization': return 'hsl(var(--chart-2))';
    case 'user': return 'hsl(var(--chart-3))';
    case 'keyword': return 'hsl(var(--chart-4))';
    default: return 'hsl(var(--muted-foreground))';
  }
};

const getNodeIcon = (type: string) => {
  switch (type) {
    case 'feed': return FileText;
    case 'organization': return Building;
    case 'user': return Users;
    case 'keyword': return Tag;
    default: return Tag;
  }
};

interface MindMapNodeProps {
  data: {
    node: GraphNode;
    isExpanded: boolean;
    onExpand: (nodeId: string, nodeType: string) => void;
  };
}

export const MindMapNode = memo(({ data }: MindMapNodeProps) => {
  const { node, isExpanded, onExpand } = data;

  const IconComponent = getNodeIcon(node.type);
  const canExpand = !isExpanded && ['feed', 'organization', 'keyword'].includes(node.type);
  
  const entityId = node.id.split('_')[1];
  const isFeed = node.type === 'feed';
  const isOrganization = node.type === 'organization';

  const NodeContent = (
    <motion.div
      layout="position"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      style={{
        borderColor: getNodeColor(node.type),
      }}
      className="relative p-4 rounded-lg border-2 shadow-lg bg-card w-[280px] cursor-pointer hover:shadow-xl hover:scale-105"
    >
      {/* 2. [핵심] 보이지 않는 Handle 컴포넌트를 추가함. */}
      {/* 이 핸들은 엣지가 들어오는 연결점(왼쪽 중앙) 역할을 함. */}
      <Handle type="target" position={Position.Left} className="!bg-transparent !border-none" />
      {/* 이 핸들은 엣지가 나가는 연결점(오른쪽 중앙) 역할을 함. */}
      <Handle type="source" position={Position.Right} className="!bg-transparent !border-none" />
      
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2 flex-1 min-w-0">
          <IconComponent
            className="w-4 h-4 flex-shrink-0"
            style={{ color: getNodeColor(node.type) }}
          />
          <span className="text-sm font-medium leading-tight truncate">{node.label}</span>
        </div>
        
        {canExpand && (
          <Button
            size="sm"
            variant="ghost"
            className="h-6 w-6 p-0 hover:bg-muted"
            onClick={(e) => {
              e.stopPropagation();
              onExpand(node.id, node.type);
            }}
            title="확장"
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        )}
      </div>

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

  if (node.type === 'feed') {
    return (
      <Link href={`/feed/${entityId}`}>
        {NodeContent}
      </Link>
    );
  }
  
  if (node.type === 'organization') {
    return (
      <Link href={`/organization/${encodeURIComponent(node.label)}`}>
        {NodeContent}
      </Link>
    );
  }

  return NodeContent;
});

MindMapNode.displayName = "MindMapNode";