//import { motion } from 'motion/react';
import { motion } from 'framer-motion';
import { useState, useEffect, useCallback } from 'react';
import { MindMapNode } from './MindMapNode';
import { ZoomPanContainer } from '@/components/mind-map/ZoomPanContainer';
import { Button } from "@/components/ui/button";
import { ArrowLeft, RotateCcw } from 'lucide-react';

interface MindMapProps {
  centerTopic: string;
  onBack: () => void;
}

interface Node {
  id: string;
  title: string;
  x: number;
  y: number;
  isCenter?: boolean;
  level: number;
  category?: number; // 색상 대신 카테고리 번호
  subtopics?: string[];
  parentId?: string;
  width: number;
  height: number;
}

// 4가지 카테고리 색상 정의 - 미니멀하고 모던한 컬러 바용
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

// 노드별 카테고리 할당 함수 - 일관된 카테고리 유지
const getNodeCategory = (nodeId: string): number => {
  // 노드 ID를 기반으로 일관된 카테고리 선택
  let hash = 0;
  for (let i = 0; i < nodeId.length; i++) {
    const char = nodeId.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash) % CATEGORY_COLORS.length;
};

// 동적 서브토픽 생성 함수
const generateSubtopics = (parentTitle: string, level: number): string[] => {
  const templates = [
    '기초 이론', '실제 응용', '최신 연구', '기술 동향', '미래 전망',
    '핵심 개념', '실무 활용', '연구 방법', '발전 과정', '주요 특징',
    '관련 기술', '응용 분야', '연구 동향', '실험 방법', '이론적 배경'
  ];
  
  const concepts = [
    '분석', '모델링', '최적화', '시뮬레이션', '검증',
    '구현', '평가', '개발', '설계', '연구'
  ];
  
  // 레벨이 깊어질수록 더 구체적인 주제 생성
  const count = Math.max(3, 6 - level);
  const subtopics: string[] = [];
  
  for (let i = 0; i < count; i++) {
    const template = templates[Math.floor(Math.random() * templates.length)];
    const concept = concepts[Math.floor(Math.random() * concepts.length)];
    subtopics.push(`${parentTitle} ${template}`);
  }
  
  return subtopics;
};

const topicData: Record<string, any> = {
  '인공지능': {
    color: 'bg-blue-100 text-blue-800',
    subtopics: [
      { 
        title: '머신러닝', 
        color: 'bg-blue-50 text-blue-700', 
        subtopics: [
          '지도학습', '비지도학습', '강화학습', '딥러닝', '앙상블 방법'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '딥러닝', 
        color: 'bg-indigo-50 text-indigo-700', 
        subtopics: [
          '신경망', 'CNN', 'RNN', 'Transformer', 'GAN'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '자연어처리', 
        color: 'bg-purple-50 text-purple-700', 
        subtopics: [
          '토큰화', '임베딩', '트랜스포머', '감정분석', '기계번역'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '컴퓨터비전', 
        color: 'bg-violet-50 text-violet-700', 
        subtopics: [
          '이미지분류', '객체탐지', '세그멘테이션', '얼굴인식', '영상처리'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: 'AI 윤리', 
        color: 'bg-pink-50 text-pink-700', 
        subtopics: [
          '편향성', '투명성', '책임성', '프라이버시', '공정성'
        ],
        hasInfiniteSubtopics: true
      }
    ]
  },
  '우주과학': {
    color: 'bg-purple-100 text-purple-800',
    subtopics: [
      { 
        title: '태양계', 
        color: 'bg-purple-50 text-purple-700', 
        subtopics: [
          '행성', '위성', '소행성', '혜성', '태양'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '별의 진화', 
        color: 'bg-indigo-50 text-indigo-700', 
        subtopics: [
          '주계열성', '적색거성', '백색왜성', '중성자별', '블랙홀'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '은하', 
        color: 'bg-blue-50 text-blue-700', 
        subtopics: [
          '나선은하', '타원은하', '불규칙은하', '은하단', '초은하단'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '암흑물질', 
        color: 'bg-slate-50 text-slate-700', 
        subtopics: [
          '암흑에너지', '중력렌즈', '구조형성', 'WIMP', '액시온'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '우주탐사', 
        color: 'bg-cyan-50 text-cyan-700', 
        subtopics: [
          '로켓', '인공위성', '우주정거장', '화성탐사', '심우주탐사'
        ],
        hasInfiniteSubtopics: true
      }
    ]
  },
  '생명과학': {
    color: 'bg-green-100 text-green-800',
    subtopics: [
      { 
        title: 'DNA', 
        color: 'bg-green-50 text-green-700', 
        subtopics: [
          'DNA 복제', 'DNA 전사', 'DNA 번역', 'DNA 수리', 'DNA 변이'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '진화', 
        color: 'bg-emerald-50 text-emerald-700', 
        subtopics: [
          '자연선택', '돌연변이', '유전적드리프트', '종분화', '적응'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '생태계', 
        color: 'bg-teal-50 text-teal-700', 
        subtopics: [
          '먹이사슬', '생물다양성', '서식지', '생태적지위', '생물군계'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '세포', 
        color: 'bg-cyan-50 text-cyan-700', 
        subtopics: [
          '미토콘드리아', '세포핵', '세포막', '엽록체', '리보솜'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '생명공학', 
        color: 'bg-lime-50 text-lime-700', 
        subtopics: [
          '유전자편집', '줄기세포', '바이오센서', '조직공학', '합성생물학'
        ],
        hasInfiniteSubtopics: true
      }
    ]
  },
  '양자역학': {
    color: 'bg-orange-100 text-orange-800',
    subtopics: [
      { 
        title: '파동-입자 이중성', 
        color: 'bg-orange-50 text-orange-700', 
        subtopics: [
          '드브로이파', '불확정성원리', '상보성', '이중슬릿실험', '광전효과'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '양자얽힘', 
        color: 'bg-red-50 text-red-700', 
        subtopics: [
          'EPR역설', '벨부등식', '비국소성', '양자텔레포테이션', '양자암호'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '슈뢰딩거 방정식', 
        color: 'bg-pink-50 text-pink-700', 
        subtopics: [
          '파동함수', '에너지고유값', '확률해석', '양자터널링', '양자조화진동자'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '양자컴퓨팅', 
        color: 'bg-yellow-50 text-yellow-700', 
        subtopics: [
          '큐비트', '양자게이트', '양자알고리즘', '양자오류정정', '양자우월성'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '양자장론', 
        color: 'bg-amber-50 text-amber-700', 
        subtopics: [
          '표준모형', '페인만다이어그램', '대칭성', '게이지이론', '양자전기역학'
        ],
        hasInfiniteSubtopics: true
      }
    ]
  },
  '기후변화': {
    color: 'bg-teal-100 text-teal-800',
    subtopics: [
      { 
        title: '온실가스', 
        color: 'bg-teal-50 text-teal-700', 
        subtopics: [
          '이산화탄소', '메탄', '아산화질소', '수증기', '오존'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '지구온난화', 
        color: 'bg-cyan-50 text-cyan-700', 
        subtopics: [
          '기온상승', '해수면상승', '극지빙하', '빙하융해', '열팽창'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '탄소순환', 
        color: 'bg-green-50 text-green-700', 
        subtopics: [
          '탄소흡수', '탄소배출', '탄소저장', '산림흡수', '해양흡수'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '재생에너지', 
        color: 'bg-yellow-50 text-yellow-700', 
        subtopics: [
          '태양광', '풍력', '수력', '지열', '바이오에너지'
        ],
        hasInfiniteSubtopics: true
      },
      { 
        title: '생물다양성', 
        color: 'bg-emerald-50 text-emerald-700', 
        subtopics: [
          '멸종위기종', '서식지파괴', '생태계변화', '종보전', '유전다양성'
        ],
        hasInfiniteSubtopics: true
      }
    ]
  }
};

export function MindMap({ centerTopic, onBack }: MindMapProps) {
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());
  const [nodes, setNodes] = useState<Node[]>([]);
  const [zoomPanKey, setZoomPanKey] = useState(0); // ZoomPanContainer 리렌더링용

  // 레이아웃 상수 - 확장된 공간에 맞게 조정
  const LEVEL_SPACING = 300;
  const NODE_SPACING = 60;
  const CENTER_X = 2200; // 확장된 영역의 중앙
  const CENTER_Y = 1800; // 확장된 영역의 중앙

  // 노드의 서브토픽 가져오기 함수
  const getNodeSubtopics = useCallback((nodeId: string, nodeTitle: string, level: number) => {
    // 초기 데이터에서 서브토픽 찾기
    const data = topicData[centerTopic];
    if (!data) return null;

    // 레벨 1 노드들
    if (nodeId.startsWith('primary-')) {
      const index = parseInt(nodeId.split('-')[1]);
      const subtopic = data.subtopics[index];
      return subtopic?.subtopics || null;
    }

    // 레벨 2 이상 노드들 - 동적 생성
    if (level >= 2) {
      return generateSubtopics(nodeTitle, level);
    }

    return null;
  }, [centerTopic]);

  // 노드 위치 계산 함수
  const calculateLayout = useCallback((expandedSet: Set<string>) => {
    const data = topicData[centerTopic];
    if (!data) return [];

    const newNodes: Node[] = [];

    // 중앙 노드
    const centerNode: Node = {
      id: 'center',
      title: centerTopic,
      x: CENTER_X,
      y: CENTER_Y,
      isCenter: true,
      level: 0,
      width: 160,
      height: 50
    };
    newNodes.push(centerNode);

    // 1레벨 노드들
    const primaryNodes = data.subtopics.map((subtopic: any, index: number) => {
      const nodeId = `primary-${index}`;
      return {
        id: nodeId,
        title: subtopic.title,
        x: CENTER_X + LEVEL_SPACING,
        y: CENTER_Y + (index - (data.subtopics.length - 1) / 2) * NODE_SPACING,
        level: 1,
        category: getNodeCategory(nodeId), // 카테고리 번호 할당
        subtopics: subtopic.subtopics,
        width: 140,
        height: 40
      };
    });
    newNodes.push(...primaryNodes);

    // 확장된 노드들의 자식 노드들 재귀적으로 생성
    const processExpandedNodes = (currentNodes: Node[]) => {
      expandedSet.forEach(expandedNodeId => {
        const parentNode = currentNodes.find(n => n.id === expandedNodeId);
        if (!parentNode) return;

        const subtopics = getNodeSubtopics(expandedNodeId, parentNode.title, parentNode.level);
        if (!subtopics) return;

        const startY = parentNode.y - (subtopics.length - 1) * NODE_SPACING / 2;

        subtopics.forEach((subtopic: string, index: number) => {
          const childId = `${expandedNodeId}-child-${index}`;
          
          // 이미 존재하는 노드는 건너뛰기
          if (currentNodes.find(n => n.id === childId)) return;

          const childNode: Node = {
            id: childId,
            title: subtopic,
            x: parentNode.x + LEVEL_SPACING,
            y: startY + index * NODE_SPACING,
            level: parentNode.level + 1,
            category: getNodeCategory(childId), // 모든 레벨에 카테고리 할당
            parentId: expandedNodeId,
            subtopics: generateSubtopics(subtopic, parentNode.level + 1), // 무한 확장을 위한 서브토픽
            width: Math.max(100, 140 - parentNode.level * 10),
            height: Math.max(32, 40 - parentNode.level * 2)
          };
          currentNodes.push(childNode);
        });
      });
    };

    processExpandedNodes(newNodes);

    // 개선된 충돌 방지 및 엣지 그룹화 알고리즘
    const adjustForCollisions = (nodes: Node[]) => {
      const adjustedNodes = [...nodes];
      
      // 레벨별로 그룹화
      const nodesByLevel: { [level: number]: Node[] } = {};
      adjustedNodes.forEach(node => {
        if (!nodesByLevel[node.level]) nodesByLevel[node.level] = [];
        nodesByLevel[node.level].push(node);
      });

      // 레벨을 순차적으로 처리 (1부터 시작)
      const levels = Object.keys(nodesByLevel).map(Number).sort((a, b) => a - b);
      
      levels.forEach(level => {
        if (level === 0) return; // 중앙 노드는 제외
        
        const levelNodes = nodesByLevel[level];
        if (!levelNodes.length) return;
        
        // 부모별로 그룹화
        const nodesByParent: { [parentId: string]: Node[] } = {};
        levelNodes.forEach(node => {
          const parentId = node.parentId || 'center';
          if (!nodesByParent[parentId]) nodesByParent[parentId] = [];
          nodesByParent[parentId].push(node);
        });
        
        // 부모 노드들의 Y 위치 순서로 정렬
        const parentIds = Object.keys(nodesByParent);
        parentIds.sort((a, b) => {
          const parentA = adjustedNodes.find(n => n.id === a);
          const parentB = adjustedNodes.find(n => n.id === b);
          return (parentA?.y || 0) - (parentB?.y || 0);
        });
        
        // 각 부모 그룹의 자식들을 배치하되, 부모 위치를 기준으로 함
        parentIds.forEach((parentId) => {
          const parentNode = adjustedNodes.find(n => n.id === parentId);
          const childNodes = nodesByParent[parentId];
          
          if (!parentNode || !childNodes.length) return;
          
          // 자식 노드들을 원래 순서대로 정렬
          childNodes.sort((a, b) => a.y - b.y);
          
          // 부모 노드를 중심으로 자식들을 대칭적으로 배치
          const groupHeight = (childNodes.length - 1) * NODE_SPACING;
          let startY = parentNode.y - groupHeight / 2;
          
          childNodes.forEach((child, index) => {
            child.y = startY + index * NODE_SPACING;
          });
        });
        
        // 같은 레벨 내에서 그룹 간 겹침 방지
        parentIds.forEach((parentId, groupIndex) => {
          if (groupIndex === 0) return;
          
          const currentGroup = nodesByParent[parentId];
          const previousParentId = parentIds[groupIndex - 1];
          const previousGroup = nodesByParent[previousParentId];
          
          if (!currentGroup.length || !previousGroup.length) return;
          
          const currentMinY = Math.min(...currentGroup.map(n => n.y));
          const previousMaxY = Math.max(...previousGroup.map(n => n.y));
          const minRequiredGap = NODE_SPACING * 0.8;
          
          // 겹침이 있으면 현재 그룹을 아래로 이동
          if (currentMinY - previousMaxY < minRequiredGap) {
            const adjustment = (previousMaxY + minRequiredGap) - currentMinY;
            currentGroup.forEach(node => {
              node.y += adjustment;
            });
            
            // 부모 노드도 함께 이동
            const parentNode = adjustedNodes.find(n => n.id === parentId);
            if (parentNode) {
              const groupCenterY = (Math.min(...currentGroup.map(n => n.y)) + 
                                  Math.max(...currentGroup.map(n => n.y))) / 2;
              parentNode.y = groupCenterY;
            }
          }
        });
        
        // 부모 노드들 간의 충돌 방지 (같은 레벨의 부모들)
        const parentNodes = adjustedNodes.filter(n => parentIds.includes(n.id));
        parentNodes.sort((a, b) => a.y - b.y);
        
        for (let i = 1; i < parentNodes.length; i++) {
          const current = parentNodes[i];
          const previous = parentNodes[i - 1];
          const minDistance = NODE_SPACING * 0.6;
          
          if (current.y - previous.y < minDistance) {
            const adjustment = minDistance - (current.y - previous.y);
            
            // 현재 부모와 그 자식들을 모두 아래로 이동
            current.y += adjustment;
            const childNodes = adjustedNodes.filter(n => n.parentId === current.id);
            childNodes.forEach(child => {
              child.y += adjustment;
            });
            
            // 이후의 모든 부모들도 함께 이동
            for (let j = i + 1; j < parentNodes.length; j++) {
              parentNodes[j].y += adjustment;
              const laterChildNodes = adjustedNodes.filter(n => n.parentId === parentNodes[j].id);
              laterChildNodes.forEach(child => {
                child.y += adjustment;
              });
            }
          }
        }
      });

      return adjustedNodes;
    };

    return adjustForCollisions(newNodes);
  }, [centerTopic, getNodeSubtopics]);

  useEffect(() => {
    setNodes(calculateLayout(expandedNodes));
  }, [centerTopic, expandedNodes, calculateLayout]);

  // 새로운 주제로 변경될 때 ZoomPanContainer 초기화
  useEffect(() => {
    setExpandedNodes(new Set());
    setZoomPanKey(prev => prev + 1); // 키 변경으로 ZoomPanContainer 재마운트
  }, [centerTopic]);

  const handleNodeClick = (nodeId: string) => {
    const node = nodes.find(n => n.id === nodeId);
    if (!node) return;

    // 모든 노드가 확장 가능하도록 (레벨 2 이상은 동적 생성)
    const hasSubtopics = node.subtopics || node.level >= 1;
    if (!hasSubtopics) return;

    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        // 축소 시 하위 노드들도 모두 축소
        const nodesToCollapse = Array.from(newSet).filter(id => id.startsWith(nodeId));
        nodesToCollapse.forEach(id => newSet.delete(id));
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const resetMap = () => {
    setExpandedNodes(new Set());
  };

  // 곡선 연결선 생성
  const createCurvedPath = (startX: number, startY: number, endX: number, endY: number) => {
    const controlX1 = startX + (endX - startX) * 0.6;
    const controlY1 = startY;
    const controlX2 = startX + (endX - startX) * 0.4;
    const controlY2 = endY;
    
    return `M ${startX} ${startY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${endX} ${endY}`;
  };

  // 연결선 생성 - 동일한 좌표계에서 정확히 연결
  const connections = nodes.filter(node => node.level > 0).map(node => {
    // 부모 노드 찾기 - parentId가 없으면 center로 간주
    const parentId = node.parentId || 'center';
    const parent = nodes.find(n => n.id === parentId);
    
    if (!parent) {
      // 부모를 찾지 못한 경우, 레벨이 하나 낮은 노드들 중에서 찾기
      const possibleParents = nodes.filter(n => n.level === node.level - 1);
      if (possibleParents.length > 0) {
        // 가장 가까운 Y 위치의 부모 선택
        const closestParent = possibleParents.reduce((closest, current) => {
          const currentDistance = Math.abs(current.y - node.y);
          const closestDistance = Math.abs(closest.y - node.y);
          return currentDistance < closestDistance ? current : closest;
        });
        
        // SVG와 노드가 같은 컨테이너에 있으므로 직접 좌표 사용
        const startX = closestParent.x + closestParent.width;
        const startY = closestParent.y + closestParent.height / 2;
        const endX = node.x;
        const endY = node.y + node.height / 2;

        return (
          <motion.path
            key={`connection-${node.id}`}
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.3 }}
            transition={{ duration: 0.5, delay: node.level * 0.05 }}
            d={createCurvedPath(startX, startY, endX, endY)}
            stroke="#94a3b8"
            strokeWidth="1.5"
            fill="none"
            className="pointer-events-none"
            strokeDasharray="3,3"
          />
        );
      }
      return null;
    }

    // SVG와 노드가 같은 컨테이너에 있으므로 직접 좌표 사용
    const startX = parent.x + parent.width;
    const startY = parent.y + parent.height / 2;
    const endX = node.x;
    const endY = node.y + node.height / 2;

    // 거리에 따른 연결선 스타일 조정
    const distance = Math.abs(startY - endY);
    const strokeWidth = distance > 200 ? "1.5" : "2";
    const opacity = distance > 200 ? 0.3 : 0.4;

    return (
      <motion.path
        key={`connection-${node.id}`}
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity }}
        transition={{ duration: 0.5, delay: node.level * 0.05 }}
        d={createCurvedPath(startX, startY, endX, endY)}
        stroke="#6366f1"
        strokeWidth={strokeWidth}
        fill="none"
        className="pointer-events-none"
      />
    );
  }).filter(Boolean);

  // 주제별 이모지 매핑
  const getTopicEmoji = (topic: string) => {
    const emojiMap: Record<string, string> = {
      '인공지능': '🤖',
      '우주과학': '🚀',
      '생명과학': '🧬',
      '양자역학': '⚛️',
      '기후변화': '🌍'
    };
    return emojiMap[topic] || '🔍';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 relative">
      {/* Main Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="absolute top-0 left-0 right-0 z-30 bg-white/95 backdrop-blur-md border-b border-gray-200/50 shadow-sm"
      >
        <div className="flex items-center justify-between px-6 py-4">
          {/* Left side - Navigation and Topic */}
          <div className="flex items-center gap-6">
            <Button
              variant="outline"
              onClick={onBack}
              className="bg-white/80 hover:bg-white shadow-md"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              메인으로
            </Button>
            
            <div className="flex items-center gap-3">
              <span className="text-2xl">{getTopicEmoji(centerTopic)}</span>
              <div>
                <h1 className="font-semibold text-gray-900">{centerTopic}</h1>
                <p className="text-sm text-gray-500">마인드맵 탐험</p>
              </div>
            </div>
          </div>

          {/* Right side - Controls */}
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={resetMap}
              className="bg-white/80 hover:bg-white shadow-md"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              모두 접기
            </Button>
            
            {/* Instructions tooltip */}
            <div className="hidden md:block bg-blue-50 text-blue-700 px-3 py-2 rounded-lg border border-blue-200">
              <p className="text-sm">
                💡 노드를 클릭하여 확장하고 무한히 탐험하세요
              </p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Mobile Instructions */}
      <div className="md:hidden absolute top-20 left-4 right-4 z-30 bg-blue-50/90 backdrop-blur-sm rounded-lg p-3 border border-blue-200">
        <p className="text-sm text-blue-700 text-center">
          💡 노드 클릭으로 확장 | 🔍 휠로 확대/축소 | 🖱️ 드래그로 이동
        </p>
      </div>

      {/* Zoom and Pan Container */}
      <ZoomPanContainer key={zoomPanKey} className="min-h-screen overflow-hidden pt-20">
        {/* Mind map container - 확장된 영역과 SVG가 모두 같은 위치에 */}
        <div 
          className="absolute z-0"
          style={{ 
            width: '8000px', 
            height: '6000px',
            left: '-2000px',
            top: '-1500px'
          }}
        >
          {/* SVG for connections - 컨테이너 내부에 배치 */}
          <svg 
            className="absolute inset-0 pointer-events-none z-5" 
            width="100%" 
            height="100%"
          >
            {connections}
          </svg>

          {/* Nodes container */}
          <div className="relative z-10 w-full h-full">
            {nodes.map(node => (
              <MindMapNode
                key={node.id}
                title={node.title}
                x={node.x}
                y={node.y}
                isCenter={node.isCenter}
                level={node.level}
                category={node.category}
                isExpanded={expandedNodes.has(node.id)}
                hasChildren={true} // 모든 노드가 확장 가능
                width={node.width}
                height={node.height}
                onClick={() => handleNodeClick(node.id)}
              />
            ))}
          </div>
        </div>
      </ZoomPanContainer>
    </div>
  );
}