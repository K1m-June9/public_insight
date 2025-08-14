"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Users } from "lucide-react";

// 1. 이 컴포넌트는 현재 외부 데이터를 받지 않으므로, props가 필요 없음
//    (나중에 기능이 추가되면 props를 정의하면 됨)
interface OrganizationCommunityProps {
  organizationName: string; // 향후 확장을 위해 남겨둘 수 있음
}

export default function OrganizationCommunity({ organizationName }: OrganizationCommunityProps) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-primary">커뮤니티</h2>
      <Card className="p-8 border-dashed border-2 border-blue-200 bg-blue-50/50 dark:bg-blue-900/20 dark:border-blue-800">
        <CardContent className="text-center space-y-4 p-0">
          <div className="flex justify-center">
            <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <Users className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-lg font-semibold text-primary">커뮤니티 기능 준비중</h3>
            <p className="text-muted-foreground">
              더 나은 소통과 참여를 위한 커뮤니티 기능을 준비하고 있습니다.
            </p>
          </div>
          
          <p className="text-sm text-muted-foreground pt-2">
            곧 여러분과 함께 소통할 수 있는 다양한 커뮤니티 기능을 선보일 예정입니다.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}