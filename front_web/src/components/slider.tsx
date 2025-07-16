"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { SliderListItem } from "@/lib/types/slider";

// 1. Props 타입 정의
interface SliderProps {
  slides?: SliderListItem[];
}

// 2. 컴포넌트가 props를 받도록 수정
export function Slider({ slides = [] }: SliderProps) {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isHovering, setIsHovering] = useState(false);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // 자동 슬라이드 기능
  useEffect(() => {
    // slides 배열이 비어있지 않을 때만 타이머 설정
    if (!isHovering && slides.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentSlide((prev) => (prev + 1) % slides.length);
      }, 3000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isHovering, slides.length]);

  const prevSlide = () => setCurrentSlide((prev) => (prev === 0 ? slides.length - 1 : prev - 1));
  const nextSlide = () => setCurrentSlide((prev) => (prev + 1) % slides.length);

  // 데이터가 없을 경우 렌더링하지 않음
  if (slides.length === 0) {
    return null;
  }

  return (
    <div className="relative bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden" onMouseEnter={() => setIsHovering(true)} onMouseLeave={() => setIsHovering(false)}>
      <div className="relative h-[350px]">
        <div className="flex transition-transform duration-500 ease-in-out h-full" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
          {slides.map((slide) => (
            <Link href={`/slider/${slide.id}`} key={slide.id} className="min-w-full h-full">
              <div className="h-full">
                <div className="relative h-[200px]">
                  {/* Base64 이미지 사용 */}
                  <Image src={`data:image/jpeg;base64,${slide.image}`} alt={slide.title} fill className="object-cover" />
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold mb-2 text-gray-900">{slide.title}</h3>
                  <p className="text-gray-600 line-clamp-3">{slide.preview}</p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
      {isHovering && (
        <>
          <Button variant="ghost" size="icon" className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={prevSlide}><ChevronLeft className="h-6 w-6" /></Button>
          <Button variant="ghost" size="icon" className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white rounded-full" onClick={nextSlide}><ChevronRight className="h-6 w-6" /></Button>
        </>
      )}
      <div className="absolute bottom-2 left-0 right-0 flex justify-center gap-2">
        {slides.map((_, index) => (
          <button key={index} className={`w-2 h-2 rounded-full ${currentSlide === index ? "bg-gray-800" : "bg-gray-300"}`} onClick={() => setCurrentSlide(index)} />
        ))}
      </div>
    </div>
  );
}