"use client";

import Link from "next/link";
import { Bell, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PinnedNoticeData } from "@/lib/types/notice";
import { formatDate } from "@/lib/utils/date";

// 1. Props 타입 정의 (기존과 동일)
interface NoticesProps {
  data?: PinnedNoticeData;
}

// 2. 컴포넌트 이름 변경 (선택사항이지만 가독성을 위해)
export function Notices({ data }: NoticesProps) {
  // 3. props로 받은 데이터 사용 (기존과 동일)
  const notices = data?.notices || [];

  return (
    <Card className="shadow-sm hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-primary" />
            <CardTitle className="text-base font-semibold">공지사항</CardTitle>
          </div>
          <Button asChild variant="outline" size="sm">
            <Link href="/notice">전체보기</Link>
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {notices.map((notice, index) => (
            <Link
              href={`/notice/${notice.id}`}
              key={notice.id}
              className="group flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div className="flex-1 min-w-0">
                {/* 첫 번째 공지사항(가장 중요한)에만 다른 스타일 적용 */}
                <h4 className="text-sm text-foreground group-hover:text-primary group-hover:font-semibold transition-colors truncate mb-1">
                  {notice.title}
                </h4>
                <p className="text-xs text-muted-foreground">
                  {formatDate(notice.created_at)}
                </p>
              </div>
              <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors flex-shrink-0" />
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}