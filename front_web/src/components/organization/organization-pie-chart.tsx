"use client";

import { useState, useEffect, useRef } from "react";
import { PieChart as PieChartComponent, Pie, Cell, Sector, ResponsiveContainer } from "recharts";
import Image from "next/image";
import Link from "next/link"
import { useOrganizationCategoriesForChartQuery, useOrganizationIconQuery } from "@/hooks/queries/useOrganizationQueries";
import { useOrganizationLatestFeedsQuery } from "@/hooks/queries/useFeedQueries";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ChevronLeft, ChevronRight } from "lucide-react";

interface OrganizationPieChartProps {
  organizationName: string;
  selectedCategoryId: number | null;
  onCategorySelect: (categoryId: number) => void;
}

const COLORS = ['#333333', '#555555', '#777777', '#999999', '#BBBBBB', '#DDDDDD'];

export default function OrganizationPieChart({ organizationName, selectedCategoryId, onCategorySelect }: OrganizationPieChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [windowSize, setWindowSize] = useState({ width: 0, height: 0 });

  const [currentSlide, setCurrentSlide] = useState(0);
  const [isHovering, setIsHovering] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const { data: categoryData, isLoading: isLoadingCategories } = useOrganizationCategoriesForChartQuery(organizationName);
  const { data: iconData, isLoading: isLoadingIcon } = useOrganizationIconQuery(organizationName);
  const { data: latestFeedsData } = useOrganizationLatestFeedsQuery(organizationName, 6); 

  const data = categoryData?.data.categories.map((cat, index) => ({
    id: cat.id,
    name: cat.name,
    value: cat.percentage,
    color: COLORS[index % COLORS.length],
  })) || [];

  const feeds = latestFeedsData?.data.feeds || [];

  useEffect(() => {
    const handleResize = () => setWindowSize({ width: window.innerWidth, height: window.innerHeight });
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

    // --- 💡 5. 슬라이더 자동 넘김 로직 추가 💡 ---
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

  const getChartSize = () => Math.max(Math.min(windowSize.width * 0.4, 500), 300);
  const getInnerRadius = () => getChartSize() * 0.2;
  const getOuterRadius = () => getChartSize() * 0.32;
  const getFontSize = () => Math.max(getChartSize() * 0.032, 12);
  const getLogoSize = () => getInnerRadius() * 1.6;

  const renderActiveShape = (props: any) => {
    const { cx, cy, innerRadius, outerRadius, startAngle, endAngle, fill, payload } = props;
    const isActive = activeIndex === props.index;
    return (
      <g>
        <text x={cx} y={cy - getChartSize() * 0.36} textAnchor="middle" fill="#333" fontSize={getFontSize() + 2} fontWeight="bold" visibility={isActive ? 'visible' : 'hidden'}>
          {`${payload.name} 자료 보기`}
        </text>
        <Sector cx={cx} cy={cy} innerRadius={innerRadius} outerRadius={isActive ? outerRadius + 10 : outerRadius} startAngle={startAngle} endAngle={endAngle} fill={fill} />
      </g>
    );
  };

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
  const handlePieClick = (data: any) => onCategorySelect(data.id);
  
  if (isLoadingCategories || isLoadingIcon) {
    return <div className="bg-gray-200 h-[500px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      {selectedCategoryId && (
        <div className="mb-4 p-2 bg-gray-100 rounded-md">
          <p className="text-sm">
            <span className="font-medium">선택된 분류:</span> {data.find(d => d.id === selectedCategoryId)?.name}
            <button onClick={() => onCategorySelect(selectedCategoryId)} className="text-gray-500 hover:text-gray-700 ml-2 text-xs underline">
              필터 해제
            </button>
          </p>
        </div>
      )}
      <div className="relative" style={{ height: `${getChartSize()}px` }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChartComponent>
            <Pie activeShape={renderActiveShape} data={data} cx="50%" cy="50%" innerRadius={getInnerRadius()} outerRadius={getOuterRadius()} dataKey="value" onMouseEnter={onPieEnter} onMouseLeave={onPieLeave} onClick={handlePieClick} cursor="pointer" label={renderCustomizedLabel} labelLine={false}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke={selectedCategoryId === entry.id ? "#000" : "none"} strokeWidth={selectedCategoryId === entry.id ? 2 : 0} />
              ))}
            </Pie>
          </PieChartComponent>
        </ResponsiveContainer>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
          <div className="relative rounded-full overflow-hidden bg-white shadow-md" style={{ height: `${getLogoSize()}px`, width: `${getLogoSize()}px` }}>
            {iconData && (
              <Image src={iconData.data.organization.icon} alt={`${organizationName} 로고`} fill className="object-contain p-2" />
            )}
          </div>
        </div>
      </div>
            {/* --- 💡 6. 최신 피드 슬라이더 JSX 추가 💡 --- */}
      <div className="mt-6 relative overflow-hidden" onMouseEnter={() => setIsHovering(true)} onMouseLeave={() => setIsHovering(false)}>
        <div className="flex transition-transform duration-500 ease-in-out" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
          {feeds.map((feed) => (
            <Link href={`/feed/${feed.id}`} key={feed.id} className="min-w-full">
              <div className="bg-gray-50 p-4 rounded-md border border-gray-100 hover:bg-gray-100 transition-colors">
                <h3 className="font-medium text-lg mb-2 line-clamp-1">{feed.title}</h3>
                {/* 기관 페이지에서는 기관명 대신 카테고리명을 보여줍니다. */}
                <Badge variant="outline" className="text-xs bg-gray-100">{feed.category.name}</Badge>
              </div>
            </Link>
          ))}
        </div>

        {isHovering && feeds.length > 1 && (
          <>
            <Button variant="ghost" size="icon" className="absolute left-0 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={prevSlide}><ChevronLeft className="h-5 w-5" /></Button>
            <Button variant="ghost" size="icon" className="absolute right-0 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={nextSlide}><ChevronRight className="h-5 w-5" /></Button>
          </>
        )}

        {feeds.length > 1 && (
          <div className="flex justify-center gap-2 mt-3">
            {feeds.map((_, index) => (
              <button key={index} className={`w-2 h-2 rounded-full ${currentSlide === index ? "bg-gray-800" : "bg-gray-300"}`} onClick={() => setCurrentSlide(index)} />
            ))}
          </div>
        )}
      </div>
      {/* --- */}
    </div>
  );
}