//import { motion } from 'motion/react';
import { motion } from 'framer-motion';
import { useState, useCallback, useRef, useEffect, ReactNode } from 'react';
import { Button } from "@/components/ui/button";
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

interface ZoomPanContainerProps {
  children: ReactNode;
  className?: string;
}

export function ZoomPanContainer({ children, className = '' }: ZoomPanContainerProps) {
  const [scale, setScale] = useState(1);
  // 초기 위치를 기본값으로 설정 (나중에 조정됨)
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [dragStartPosition, setDragStartPosition] = useState({ x: 0, y: 0 });
  const [isInitialized, setIsInitialized] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const handleWheel = useCallback((e: WheelEvent) => {
    e.preventDefault();
    
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    const newScale = Math.max(0.1, Math.min(3, scale + delta));
    
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      const mouseX = e.clientX - rect.left;
      const mouseY = e.clientY - rect.top;
      
      // 마우스 위치를 중심으로 줌
      const scaleRatio = newScale / scale;
      const newPosition = {
        x: mouseX - (mouseX - position.x) * scaleRatio,
        y: mouseY - (mouseY - position.y) * scaleRatio
      };
      
      setScale(newScale);
      setPosition(newPosition);
    }
  }, [scale, position]);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    // 좌클릭이고, 노드가 아닌 배경 영역에서만 드래그 시작
    if (e.button === 0) {
      const target = e.target as HTMLElement;
      // 노드나 버튼이 아닌 배경 영역인지 확인
      const isBackgroundClick = !target.closest('[data-node]') && 
                               !target.closest('button') && 
                               !target.closest('[role="button"]');
      
      if (isBackgroundClick) {
        setIsDragging(true);
        setDragStart({ x: e.clientX, y: e.clientY });
        setDragStartPosition(position);
        e.preventDefault();
      }
    }
  }, [position]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (isDragging) {
      const deltaX = e.clientX - dragStart.x;
      const deltaY = e.clientY - dragStart.y;
      
      setPosition({
        x: dragStartPosition.x + deltaX,
        y: dragStartPosition.y + deltaY
      });
    }
  }, [isDragging, dragStart, dragStartPosition]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const zoomIn = useCallback(() => {
    const newScale = Math.min(3, scale + 0.2);
    setScale(newScale);
  }, [scale]);

  const zoomOut = useCallback(() => {
    const newScale = Math.max(0.1, scale - 0.2);
    setScale(newScale);
  }, [scale]);

  const centerViewOnMindMap = useCallback(() => {
    const container = containerRef.current;
    if (container) {
      const rect = container.getBoundingClientRect();
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      setPosition({ 
        x: centerX-800, 
        y: centerY-500 
      });
      setIsInitialized(true);
    }
  }, []);

  const resetView = useCallback(() => {
    setScale(1);
    centerViewOnMindMap();
  }, [centerViewOnMindMap]);

  // 컴포넌트 마운트 시 중앙 노드를 화면 중앙에 위치시키기
  useEffect(() => {
    const timer = setTimeout(() => {
      centerViewOnMindMap();
    }, 100); // 약간의 지연을 두어 DOM이 완전히 렌더링된 후 실행
    
    return () => clearTimeout(timer);
  }, [centerViewOnMindMap]);

  // 윈도우 리사이즈 시에도 중앙 정렬 유지
  useEffect(() => {
    const handleResize = () => {
      if (isInitialized) {
        centerViewOnMindMap();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [centerViewOnMindMap, isInitialized]);

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener('wheel', handleWheel, { passive: false });
      return () => container.removeEventListener('wheel', handleWheel);
    }
  }, [handleWheel]);

  // 전역 마우스 이벤트 리스너 추가 (드래그 중 마우스가 컨테이너 밖으로 나가도 추적)
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'grabbing';
      document.body.style.userSelect = 'none';
      
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      };
    }
  }, [isDragging, handleMouseMove, handleMouseUp]);

  return (
    <div 
      ref={containerRef}
      className={`relative overflow-hidden ${className}`}
      onMouseDown={handleMouseDown}
      style={{ 
        cursor: isDragging ? 'grabbing' : 'grab',
        backgroundColor: '#f8fafc'
      }}
    >
      {/* Zoom Controls */}
      <div className="absolute bottom-6 right-6 z-30 flex flex-col gap-2">
        <Button
          variant="outline"
          size="icon"
          onClick={zoomIn}
          className="bg-white/90 backdrop-blur-sm shadow-lg hover:bg-white"
        >
          <ZoomIn className="w-4 h-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={zoomOut}
          className="bg-white/90 backdrop-blur-sm shadow-lg hover:bg-white"
        >
          <ZoomOut className="w-4 h-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={resetView}
          className="bg-white/90 backdrop-blur-sm shadow-lg hover:bg-white"
        >
          <RotateCcw className="w-4 h-4" />
        </Button>
      </div>

      {/* Zoom Level Indicator */}
      <div className="absolute bottom-6 left-6 z-30 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg">
        <span className="text-sm font-medium text-gray-700">
          {Math.round(scale * 100)}%
        </span>
      </div>

      {/* Infinite Grid Background */}
      <motion.div
        animate={{
          scale,
          x: position.x,
          y: position.y
        }}
        transition={{
          type: "tween",
          duration: 0.1
        }}
        className="absolute inset-0 pointer-events-none"
        style={{
          transformOrigin: '0 0',
          backgroundImage: `
            linear-gradient(to right, rgba(99, 102, 241, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(99, 102, 241, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px',
          width: '15000px',
          height: '12000px',
          left: '-7500px',
          top: '-6000px'
        }}
      />

      {/* Transform Container */}
      <motion.div
        animate={{
          scale,
          x: position.x,
          y: position.y
        }}
        transition={{
          type: "tween",
          duration: 0.1
        }}
        className="transform-gpu relative z-10"
        style={{
          transformOrigin: '0 0'
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}