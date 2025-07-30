"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { PieChart as PieChartComponent, Pie, Cell, Sector, ResponsiveContainer } from "recharts";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { OrganizationListData } from "@/lib/types/organization";
import { LatestFeedData } from "@/lib/types/feed";

interface PieChartProps {
  chartData?: OrganizationListData;
  latestFeeds?: LatestFeedData;
}

const COLORS = ['#333333', '#555555', '#777777', '#999999', '#BBBBBB', '#DDDDDD'];

export function PieChart({ chartData, latestFeeds }: PieChartProps) {
  const router = useRouter();
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isHovering, setIsHovering] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  const data = chartData?.organizations.map((org, index) => ({
    name: org.name,
    value: org.percentage,
    color: COLORS[index % COLORS.length]
  })) || [];
  const feeds = latestFeeds?.feeds || [];

  useEffect(() => {
    const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const getChartSize = () => Math.max(Math.min(windowSize.width * 0.4, 500), 300);
  const getInnerRadius = () => getChartSize() * 0.2;
  const getOuterRadius = () => getChartSize() * 0.32;
  const getFontSize = () => Math.max(getChartSize() * 0.032, 12);

  useEffect(() => {
    if (!isHovering && feeds.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % feeds.length);
      }, 3000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isHovering, feeds.length]);

  const prevSlide = () => setCurrentSlide((prev) => (prev === 0 ? feeds.length - 1 : prev - 1));
  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % feeds.length);

  // --- 💡 여기가 핵심 수정 부분 💡 ---
  const renderActiveShape = (props: any) => {
    const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload, ...rest } = props; // percent, value 없앰
    
    // 현재 렌더링되는 섹터가 활성화된 섹터인지 직접 확인
    const isActive = activeIndex === rest.index;

    return (
      <g>
        <text x={cx} y={cy - getChartSize() * 0.36} textAnchor="middle" fill="#333" fontSize={getFontSize() + 2} fontWeight="bold" visibility={isActive ? 'visible' : 'hidden'}>
          {`${payload.name} 페이지로 이동`}
        </text>
        <Sector
          cx={cx}
          cy={cy}
          innerRadius={innerRadius}
          // 활성화된 섹터만 더 크게 표시
          outerRadius={isActive ? outerRadius + 35 : outerRadius}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
        />
      </g>
    );
  };
  // --- 수정 끝 ---

  const renderCustomizedLabel = (props: any) => {
    const { cx, cy, midAngle, outerRadius, fill, payload } = props;
    const RADIAN = Math.PI / 180;
    const sin = Math.sin(-RADIAN * midAngle);
    const cos = Math.cos(-RADIAN * midAngle);
    const labelDistance = getChartSize() * 0.06;
    const lineLength = getChartSize() * 0.04;
    const x1 = cx + outerRadius * cos;
    const y1 = cy + outerRadius * sin;
    const x2 = cx + (outerRadius + labelDistance) * cos;
    const y2 = cy + (outerRadius + labelDistance) * sin;
    const x3 = x2 + (cos >= 0 ? lineLength : -lineLength);

    return (
      <g>
        <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={fill} />
        <line x1={x2} y1={y2} x2={x3} y2={y2} stroke={fill} />
        <text x={x3 + (cos >= 0 ? 5 : -5)} y={y2} textAnchor={cos >= 0 ? "start" : "end"} fill="#333" fontSize={getFontSize()}>
          {payload.name}
        </text>
      </g>
    );
  };
  
  const onPieEnter = (_: any, index: number) => setActiveIndex(index);
  const onPieLeave = () => setActiveIndex(null);
  const handlePieClick = (data: any) => router.push(`/organization/${data.name}`);

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="relative" style={{ height: `${getChartSize()}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChartComponent>
            {/* --- 💡 여기가 핵심 수정 부분 💡 --- */}
            <Pie
              // activeIndex prop을 완전히 제거합니다.
              activeShape={renderActiveShape}
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={getInnerRadius()}
              outerRadius={getOuterRadius()}
              dataKey="value"
              onMouseEnter={onPieEnter}
              onMouseLeave={onPieLeave}
              onClick={handlePieClick}
              cursor="pointer"
              label={renderCustomizedLabel}
              labelLine={false}
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
             {/* --- 수정 끝 --- */}
          </PieChartComponent>
        </ResponsiveContainer>
      </div>
      {/* ... 이하 슬라이더 부분은 이전과 동일 ... */}
      <div
        className="mt-6 relative overflow-hidden"
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        <div
          className="flex transition-transform duration-500 ease-in-out"
          style={{ transform: `translateX(-${currentSlide * 100}%)` }}
        >
          {feeds.map((feed) => (
            <Link href={`/feed/${feed.id}`} key={feed.id} className="min-w-full">
              <div className="bg-gray-50 p-4 rounded-md border border-gray-100 hover:bg-gray-100 transition-colors">
                <h3 className="font-medium text-lg mb-2 line-clamp-1">{feed.title}</h3>
                <Badge variant="outline" className="text-xs bg-gray-100">
                  {feed.organization.name}
                </Badge>
              </div>
            </Link>
          ))}
        </div>

        {isHovering && (
          <>
            <Button variant="ghost" size="icon" className="absolute left-0 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={prevSlide}>
              <ChevronLeft className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="absolute right-0 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={nextSlide}>
              <ChevronRight className="h-5 w-5" />
            </Button>
          </>
        )}

        <div className="flex justify-center gap-2 mt-3">
          {feeds.map((_, index) => (
            <button
              key={index}
              className={`w-2 h-2 rounded-full ${currentSlide === index ? "bg-gray-800" : "bg-gray-300"}`}
              onClick={() => setCurrentSlide(index)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}