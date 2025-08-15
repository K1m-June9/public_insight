"use client";

import Link from "next/link";
import { Building, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress"; // 💡 Progress Bar 컴포넌트 사용
import { OrganizationListData } from "@/lib/types/organization";

// 1. Props 타입 정의: 이제 chartData만 필요합니다.
interface OrganizationListProps {
  chartData?: OrganizationListData;
}

// 2. 컴포넌트 이름 및 props 변경
export function OrganizationList({ chartData }: OrganizationListProps) {
  
  // 3. 불필요한 상태와 로직 모두 제거 (router, useState, useEffect 등)
  
  // 4. props로 받은 데이터를 가공
  // "기타" 항목은 백엔드에서 오므로, 여기서는 별도 처리X
  const organizations = chartData?.organizations || [];

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <Building className="w-5 h-5 text-primary" />
          <CardTitle className="text-base font-semibold">기관별 보유 데이터 현황</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {organizations.map((org) => (
            // 5. Link 컴포넌트로 각 항목을 감싸서 페이지 이동 기능 구현
            <Link
              href={org.name === "기타" ? "#" : `/organization/${org.name}`}
              key={org.id}
              className={`block p-3 rounded-md transition-colors group ${org.name !== "기타" ? "hover:bg-accent cursor-pointer" : "cursor-default"}`}
              aria-disabled={org.name === "기타"}
              onClick={(e) => { if (org.name === "기타") e.preventDefault(); }}
            >
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-foreground group-hover:text-primary transition-colors">
                  {org.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-muted-foreground w-8 text-right">{org.percentage}%</span>
                  {org.name !== "기타" && (
                    <ExternalLink className="w-3 h-3 text-muted-foreground group-hover:text-primary transition-colors" />
                  )}
                </div>
              </div>
              {/* 6. 퍼센트 바(Progress Bar) 추가 */}
              <Progress value={org.percentage} className="h-1 mt-2" />
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}