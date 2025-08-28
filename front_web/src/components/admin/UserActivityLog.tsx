"use client";

import { useAdminUserActivitiesInfiniteQuery } from "@/hooks/queries/useAdminUserQueries";
import { formatDate } from "@/lib/utils/date";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function UserActivityLog({ userId }: { userId: string }) {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, isError } = useAdminUserActivitiesInfiniteQuery(userId);

  return (
    <Card>
      <CardHeader><CardTitle>활동 로그</CardTitle></CardHeader>
        <CardContent>
        {isLoading ? (<div className="text-center py-10">로그를 불러오는 중...</div>)
        : isError ? (<div className="text-center py-10 text-destructive">로그를 불러오는 데 실패했습니다.</div>)
        : (data && data.pages[0].data.activities.length > 0) ? (
            <div className="space-y-4">
            {data.pages.map((page, i) => (
                <div key={i} className="space-y-2">
                {page.data.activities.map(activity => (
                    <div key={activity.id} className="flex items-start text-sm border-b pb-2">
                    <div className="w-40 text-muted-foreground">{formatDate(activity.created_at, 'YYYY-MM-DD HH:mm')}</div>
                    <div className="flex-1">
                        <span className="font-semibold">{activity.activity_type}</span>
                        <p className="text-xs text-muted-foreground break-all">IP: {activity.ip_address} / Target: {activity.target_id || 'N/A'}</p>
                    </div>
                    </div>
                ))}
                </div>
            ))}
            {hasNextPage && (
                <Button onClick={() => fetchNextPage()} disabled={isFetchingNextPage} className="w-full mt-4">
                {isFetchingNextPage ? '불러오는 중...' : '더보기'}
                </Button>
            )}
            {!hasNextPage && (
                <p className="text-center text-sm text-muted-foreground pt-4">마지막 로그입니다.</p>
            )}
            </div>
        ) : (
            <p className="text-center text-sm text-muted-foreground py-10">활동 로그가 없습니다.</p>
        )}
        </CardContent>
    </Card>
  );
}