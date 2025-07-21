"use client";

import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import { ArrowLeft } from "lucide-react";
import { useSliderDetailQuery } from "@/hooks/queries/useSliderQueries";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils/date";

export default function SliderDetailPage() {
  const router = useRouter();
  const params = useParams();
  
  // 1. URL 파라미터에서 id를 가져와 숫자로 변환
  const sliderId = Number(params.id);

  // 2. useSliderDetailQuery 훅을 사용하여 데이터를 불러d옴
  // sliderId가 유효한 숫자일 때만 쿼리를 활성화(enabled)
  const { data: sliderData, isLoading, isError } = useSliderDetailQuery(sliderId, {
    enabled: !isNaN(sliderId) && sliderId > 0,
  });
  
  // 3. 훅에서 반환된 데이터 구조에 맞게 slider 변수를 할당
  const slider = sliderData?.data.slider;

  // 뒤로 가기
  const goBack = () => {
    router.back();
  };

  if (isLoading) {
    return (
      <div className="container px-4 py-8 md:px-6">
        <div className="flex justify-center items-center h-[60vh]">
          <div className="animate-pulse text-gray-500">로딩 중...</div>
        </div>
      </div>
    );
  }

  if (isError || !slider) {
    return (
      <div className="container px-4 py-8 md:px-6">
        <div className="flex flex-col justify-center items-center h-[60vh] gap-4">
          <p className="text-gray-500">슬라이더 내용을 찾을 수 없습니다.</p>
          <Button variant="outline" onClick={() => router.push('/')}>메인으로 돌아가기</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="container px-4 py-8 md:px-6">
      <div className="max-w-4xl mx-auto">
        {/* 뒤로가기 버튼 */}
        <Button variant="ghost" onClick={goBack} className="mb-6 flex items-center gap-1">
          <ArrowLeft className="h-4 w-4" />
          <span>뒤로가기</span>
        </Button>

        {/* 배경 이미지 */}
        <div className="relative h-[400px] w-full mb-6 rounded-lg overflow-hidden">
          {/* Base64 이미지를 사용 */}
          <Image src={`data:image/jpeg;base64,${slider.image}`} alt={slider.title} fill className="object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex flex-col justify-end p-8">
            <Badge className="mb-3 self-start">{slider.tag}</Badge>
            <h1 className="text-3xl font-bold text-white mb-2">{slider.title}</h1>
            <div className="flex items-center text-white/80 text-sm">
              <span>{slider.author}</span>
              <span className="mx-2">•</span>
              <span>{formatDate(slider.created_at)}</span>
            </div>
          </div>
        </div>
        {/* 본문 내용 */}
        <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
          {/* 
            'prose' 클래스는 h1, p, ul 등의 태그에 자동으로 스타일을 입혀주는 역할
            일반 텍스트를 표시할 때는 필요하지 않지만, 줄바꿈 등을 위해 남겨둘 수 있음
            또는 Tailwind CSS의 whitespace-pre-wrap 클래스를 사용하여 줄바꿈을 유지할 수 있음.
            현재는 그냥 평문
            <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: slider.content }} /> <- 예전거(나중에 필요해지면 쓸까 싶어서 그냥 남겨둠)
          */}
          <div className="prose max-w-none">
            <p className="whitespace-pre-wrap">{slider.content}</p>
          </div>
        </div>
      </div>
    </div>
  );
}