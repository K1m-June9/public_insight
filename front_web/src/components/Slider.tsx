"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SliderListItem } from "@/lib/types/slider";
import { formatDate } from "@/lib/utils/date";

// 1. Props 타입 정의 (기존과 동일)
interface SliderProps {
  slides?: SliderListItem[];
}

export function Slider({ slides = [] }: SliderProps) {
  // 2. 캐러셀 로직은 모두 그대로 유지
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isHovering, setIsHovering] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!isHovering && slides.length > 1) { // 슬라이드가 2개 이상일 때만 자동 실행
      intervalRef.current = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
      }, 5000); 
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isHovering, slides.length]);

  const prevSlide = () => setCurrentSlide((prev) => (prev === 0 ? slides.length - 1 : prev - 1));
  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);

  const getSlideImageUrl = (filename: string) => {
    if (!filename) return 'https://www.public-insight.co.kr/static/sliders/default.jpg'; // 기본 이미지
    return `https://www.public-insight.co.kr/static/sliders/${filename}`; // public/static/sliders/ 아래 실제 파일 위치
  };


  if (slides.length === 0) {
    // 데이터가 없을 때 보여줄 UI (스켈레톤 또는 메시지)
    return <div className="bg-gray-200 h-[450px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  return (
    // 3. 최상위 div에 캐러셀 로직을 위한 onMouseEnter/Leave를 추가
    <div 
      className="relative rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow"
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={() => setIsHovering(false)}
    >
      {/* 슬라이드 컨테이너 */}
      <div className="flex transition-transform duration-500 ease-in-out" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
        {slides.map((slide) => (
          <article key={slide.id} className="min-w-full bg-card border border-border">
            {/* 이미지 영역 */}
            <Link href={`/slider/${slide.id}`} className="block relative">
              {/* --- 💡 1. image_path를 imageUrl로 수정 💡 --- */}
              <Image
                src={getSlideImageUrl(slide.imageUrl)} 
                alt={slide.title}
                width={800}
                height={400}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <div className="absolute bottom-4 left-4 right-4 text-white">
                <h2 className="text-xl text-white leading-tight">{slide.title}</h2>
              </div>
            </Link>

            {/* 텍스트 영역 */}
            <div className="p-6">
              <p className="text-muted-foreground leading-relaxed text-sm line-clamp-2">{slide.preview}</p>
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
                <span className="text-sm text-muted-foreground">{formatDate(slide.created_at)}</span>
                <Button asChild variant="ghost" size="sm" className="text-primary hover:text-primary/80">
                  <Link href={`/slider/${slide.id}`}>자세히 보기</Link>
                </Button>
              </div>
            </div>
          </article>
        ))}
      </div>

      {/* 좌우 이동 버튼 (호버 시 표시) */}
      {isHovering && slides.length > 1 && (
        <>
          <Button variant="ghost" size="icon" className="absolute left-2 top-[128px] -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={prevSlide}><ChevronLeft className="h-6 w-6" /></Button>
          <Button variant="ghost" size="icon" className="absolute right-2 top-[128px] -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={nextSlide}><ChevronRight className="h-6 w-6" /></Button>
        </>
      )}

      {/* 인디케이터 (점) */}
      {slides.length > 1 && (
        <div className="absolute bottom-[220px] left-0 right-0 flex justify-center gap-2">
            {slides.map((_, index) => (
            <button key={index} className={`w-2 h-2 rounded-full transition-colors ${currentSlide === index ? "bg-white" : "bg-white/50"}`} onClick={() => setCurrentSlide(index)} />
            ))}
        </div>
      )}
    </div>
  );
}