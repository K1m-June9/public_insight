//import { motion } from 'motion/react';
import { motion } from 'framer-motion';
import { useState } from 'react';
import { ChevronRight, ChevronDown } from 'lucide-react';

interface MindMapNodeProps {
  title: string;
  x: number;
  y: number;
  isCenter?: boolean;
  level?: number;
  category?: number; // 색상 대신 카테고리 번호
  onClick?: () => void;
  isExpanded?: boolean;
  hasChildren?: boolean;
  width?: number;
  height?: number;
}

// 카테고리 색상 정의
const CATEGORY_COLORS = [
  {
    bar: 'bg-blue-500',
    hover: 'hover:bg-blue-50 hover:border-blue-200',
    accent: 'bg-blue-500'
  },
  {
    bar: 'bg-amber-500', 
    hover: 'hover:bg-amber-50 hover:border-amber-200',
    accent: 'bg-amber-500'
  },
  {
    bar: 'bg-emerald-500',
    hover: 'hover:bg-emerald-50 hover:border-emerald-200', 
    accent: 'bg-emerald-500'
  },
  {
    bar: 'bg-orange-500',
    hover: 'hover:bg-orange-50 hover:border-orange-200',
    accent: 'bg-orange-500'
  }
];

export function MindMapNode({ 
  title, 
  x, 
  y, 
  isCenter = false, 
  level = 1,
  category,
  onClick,
  isExpanded = false,
  hasChildren = false,
  width = 140,
  height = 40
}: MindMapNodeProps) {
  const [isHovered, setIsHovered] = useState(false);

  // 노드 스타일 설정 - 깔끔하고 모던한 디자인
  const getNodeStyle = () => {
    if (isCenter) {
      return 'bg-white border-indigo-200 text-gray-900 shadow-md';
    }
    
    // 일반 노드는 깔끔한 흰색 베이스
    const baseStyle = 'bg-white border-gray-200 text-gray-900 shadow-sm';
    
    // 카테고리별 호버 효과
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
      {/* Main Node */}
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
        {/* 카테고리 컬러 바 - 왼쪽에 얇은 세로줄 */}
        {!isCenter && category !== undefined && (
          <div 
            className={`absolute left-0 top-0 bottom-0 w-1 ${CATEGORY_COLORS[category % CATEGORY_COLORS.length].bar}`}
          />
        )}
        
        {/* 노드 내용 */}
        <div className="flex items-center px-3 py-2 w-full">
          <span className={`${getTextSize()} font-medium text-left leading-tight flex-1`}>
            {title}
          </span>
        </div>
      </div>

      {/* External Expand/Collapse Button - 노드 오른쪽 외부에 위치 */}
      {hasChildren && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: isHovered ? 1 : 0.7 }}
          transition={{ duration: 0.2 }}
          className="absolute cursor-pointer"
          style={{
            left: width + 8, // 노드 너비 + 간격
            top: height / 2 - 10, // 노드 중앙에 위치
            zIndex: 10
          }}
          onClick={(e) => {
            e.stopPropagation();
            onClick?.();
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
      
      {/* Center node glow effect - 더 세련되게 */}
      {isCenter && (
        <motion.div
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