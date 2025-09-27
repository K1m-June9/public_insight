"use client";

import { Cloud } from "lucide-react";
// 🔧 [1. 수정] 새로운 커스텀 훅을 임포트
import { useWordCloudQuery } from "@/hooks/queries/useGraphQueries";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link"; // 👈 [추가] 키워드 클릭 시 페이지 이동을 위해 Link 컴포넌트 임포트

// 🔧 [2. 추가] 색상과 굵기를 동적으로 계산하기 위한 헬퍼 상수
const COLOR_PALETTE = [
  "hsl(var(--primary))",
  "hsl(var(--secondary-foreground))",
  "hsl(var(--chart-2))",
  "hsl(var(--chart-3))",
  "hsl(var(--chart-4))",
];
const FONT_WEIGHTS = [300, 400, 500, 600, 700];

interface OrganizationWordCloudProps {
  organizationName: string;
}

export default function OrganizationWordCloud({ organizationName }: OrganizationWordCloudProps) {
  // 🔧 [3. 수정] 새로운 useWordCloudQuery 훅을 사용
  const { data: response, isLoading, isError } = useWordCloudQuery(
    {
      organizationName,
      limit: 20, // 기관 페이지에서는 20개 정도가 적당해 보임 (튜닝 가능)
    },
    {
      enabled: !!organizationName, // organizationName이 있을 때만 쿼리 실행
    }
  );

  // 🔧 [4. 수정] API 응답 구조 변경에 따라 키워드 목록을 가져오는 방식 변경
  const keywords = response?.data || [];

  // 로딩 상태 UI (기존과 동일)
  if (isLoading) {
    return <div className="bg-gray-200 h-[300px] rounded-lg shadow-sm border border-gray-200 animate-pulse"></div>;
  }

  // 에러 상태 UI (기존과 동일)
  if (isError) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center space-x-2">
            <Cloud className="w-5 h-5 text-destructive" />
            <CardTitle className="text-base font-semibold text-destructive">주요 키워드</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-center text-sm text-muted-foreground py-8">데이터를 불러오는 데 실패했습니다.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow p-6">
      <CardHeader className="p-0 mb-4"> {/* 👈 mb-4로 간격 살짝 조정 */}
        <div className="flex items-center space-x-2">
          <Cloud className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">주요 키워드</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {keywords.length > 0 ? (
          <div className="relative h-64 flex flex-wrap content-center items-center justify-center gap-x-4 gap-y-2 overflow-hidden">
            {/* 🔧 [5. 수정] 새로운 데이터(text, value)를 사용하고, 동적으로 스타일과 링크를 적용 */}
            {keywords.map((word, index) => (
              <Link href={`/explore?keyword=${encodeURIComponent(word.text)}`} key={word.text}>
                <span
                  className="inline-block transition-all duration-300 hover:scale-110 hover:z-10 cursor-pointer"
                  style={{
                    // 'value' (인기 점수)를 기반으로 폰트 크기를 동적으로 계산 (12px ~ 28px)
                    // value의 최대/최소값을 알면 더 정교한 스케일링 가능
                    fontSize: `${12 + Math.min(word.value / 5, 16)}px`,
                    // 미리 정의된 색상 팔레트에서 순환하며 색상 적용
                    color: COLOR_PALETTE[index % COLOR_PALETTE.length],
                    // 폰트 굵기도 순환하며 적용
                    fontWeight: FONT_WEIGHTS[index % FONT_WEIGHTS.length],
                  }}
                >
                  {word.text}
                </span>
              </Link>
            ))}
          </div>
        ) : (
          <div className="relative h-64 flex items-center justify-center">
            <p className="text-muted-foreground">표시할 주요 키워드가 없습니다.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}