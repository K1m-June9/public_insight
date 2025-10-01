'use client'; 

import { motion } from 'framer-motion';
import { useState } from 'react';
import { ChevronRight, ChevronDown, FileText, Building2, Tag } from 'lucide-react';
import type { FC } from 'react';

// 카테고리별 아이콘을 렌더링하는 작은 헬퍼 컴포넌트
const CategoryIcon: FC<{ category?: number }> = ({ category }) => {
  if (category === undefined) return null;

  // 나중에 노드 종류 추가할듯
  switch (category) {
    case 0: // Feed (파랑)
      return <FileText className="w-4 h-4 text-blue-500" />;
    case 1: // Organization (주황)
      return <Building2 className="w-4 h-4 text-orange-500" />;
    case 2: // Keyword (초록)
      return <Tag className="w-4 h-4 text-emerald-500" />;
    default:
      return null;
  }
};

interface MindMapNodeProps {
  title: string;
  x: number;
  y: number;
  isCenter?: boolean;
  level?: number;
  category?: number;
  onClick?: () => void;
  handleExpandClick?: () => void;
  isExpanded?: boolean;
  hasChildren?: boolean;
  width?: number;
  height?: number;
}

const CATEGORY_COLORS = [
  // Category 0: Feed (파랑 계열)
  {
    bar: 'bg-blue-500',
    hover: 'hover:bg-blue-50 hover:border-blue-200',
  },
  // Category 1: Organization (주황 계열)
  {
    bar: 'bg-orange-500',
    hover: 'hover:bg-orange-50 hover:border-orange-200',
  },
  // Category 2: Keyword (초록 계열)
  {
    bar: 'bg-emerald-500',
    hover: 'hover:bg-emerald-50 hover:border-emerald-200', 
  },
  // Category 3: 기타 (회색 계열)
  {
    bar: 'bg-slate-500',
    hover: 'hover:bg-slate-50 hover:border-slate-200',
  }
];

export function MindMapNode({ 
  title, x, y, isCenter = false, level = 1, category,
  onClick, handleExpandClick, isExpanded = false, hasChildren = false,
  width = 140, height = 40
}: MindMapNodeProps) {
  const [isHovered, setIsHovered] = useState(false);

  const getNodeStyle = () => {
    if (isCenter) {
      return 'bg-white border-indigo-200 text-gray-900 shadow-md';
    }
    const baseStyle = 'bg-white border-gray-200 text-gray-900 shadow-sm';
    if (category !== undefined) {
      const categoryColor = CATEGORY_COLORS[category % CATEGORY_COLORS.length];
      return `${baseStyle} ${categoryColor.hover} transition-all duration-200`;
    }
    return `${baseStyle} hover:bg-gray-50 hover:border-gray-300 transition-all duration-200`;
  };

  const getTextSize = () => {
    if (isCenter) return 'text-base';
    if (level === 1) return 'text-sm';
    return 'text-xs';
  };

  return (
    <motion.div
      // (motion.div의 props는 변경 없음)
      initial={{ scale: 0, opacity: 0, x: x - 50 }}
      animate={{ scale: 1, opacity: 1, x, y }}
      transition={{ 
        type: "spring", 
        stiffness: 300, 
        damping: 25,
        delay: isCenter ? 0 : level * 0.05
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className="absolute select-none"
      style={{
        left: 0,
        top: 0,
        transform: `translate(${x}px, ${y}px)`
      }}
      data-node="true"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div 
        className={`
          rounded-lg flex items-center cursor-pointer relative overflow-hidden
          border ${getNodeStyle()}
          ${isHovered ? 'shadow-md' : ''}
          ${isExpanded ? 'ring-2 ring-blue-200 ring-opacity-50' : ''}
        `}
        style={{ width, height }}
        onClick={onClick}
      >
        {!isCenter && category !== undefined && (
          <div 
            className={`absolute left-0 top-0 bottom-0 w-1 ${CATEGORY_COLORS[category % CATEGORY_COLORS.length].bar}`}
          />
        )}
        
        {/* ================================================================= */}
        {/* [핵심 수정] 아이콘 추가를 위해 JSX 구조 변경 */}
        <div className="flex items-center pl-3 pr-2 py-1 w-full gap-2"> {/* padding 및 gap 수정 */}
          {!isCenter && <CategoryIcon category={category} />}
          <span className={`${getTextSize()} font-medium text-left leading-tight flex-1`}>
            {title}
          </span>
        </div>
        {/* ================================================================= */}

      </div>
      {hasChildren && (
        <motion.div
          // (확장 버튼 motion.div의 props는 변경 없음)
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: isHovered ? 1 : 0.7 }}
          transition={{ duration: 0.2 }}
          className="absolute cursor-pointer"
          style={{
            left: width + 8,
            top: height / 2 - 10,
            zIndex: 10
          }}
          onClick={(e) => {
            e.stopPropagation();
            handleExpandClick?.();
          }}
        >
          <div 
            className={`
              w-5 h-5 rounded-full border-2 bg-white shadow-md
              flex items-center justify-center transition-all duration-200
              hover:scale-110 active:scale-95
              ${isExpanded 
                ? 'border-blue-400 text-blue-600 bg-blue-50' 
                : 'border-gray-300 text-gray-500 hover:border-gray-400 hover:text-gray-600'
              }
            `}
          >
            {isExpanded ? (
              <ChevronDown className="w-3 h-3" />
            ) : (
              <ChevronRight className="w-3 h-3" />
            )}
          </div>
        </motion.div>
      )}
      {isCenter && (
        <motion.div
          // (중앙 노드 효과 motion.div의 props는 변경 없음)
          className="absolute rounded-lg bg-indigo-200 opacity-15 -z-10"
          style={{ 
            width: width + 8, 
            height: height + 8,
            left: -4,
            top: -4
          }}
          animate={{ 
            scale: [1, 1.02, 1],
            opacity: [0.15, 0.25, 0.15]
          }}
          transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
        />
      )}
    </motion.div>
  );
}