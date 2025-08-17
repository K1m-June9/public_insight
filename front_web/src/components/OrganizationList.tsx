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
  const organizations = chartData?.organizations || [];

  return (
    <Card className="bg-card border border-border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      <CardHeader className="p-0 mb-0"> 
        <div className="flex items-center space-x-2">
          <Building className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">기관별 자료 보유 현황</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="space-y-2">
          {organizations.map((org) => (
            <Link
              href={org.name === "기타" ? "#" : `/organization/${org.name}`}
              key={org.id}
              className={`block p-3 rounded-md transition-colors group ${org.name !== "기타" ? "hover:bg-accent cursor-pointer" : "cursor-default"}`}
              aria-disabled={org.name === "기타"}
              onClick={(e) => { if (org.name === "기타") e.preventDefault(); }}
            >
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground group-hover:text-primary transition-colors">
                  {org.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-muted-foreground w-12 text-right">{Number(org.percentage).toFixed(1)}%</span>
                  {org.name !== "기타" && (
                    <ExternalLink className="w-3 h-3 text-muted-foreground group-hover:text-primary transition-colors" />
                  )}
                </div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}