"use client";

import { useParams } from 'next/navigation';
import { useAdminUserDetailQuery } from "@/hooks/queries/useAdminUserQueries";
import Link from "next/link";

// UI Components
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";

// Child Components
import { UserInfoCard } from "@/components/admin/UserInfoCard";
import { UserActivityLog } from "@/components/admin/UserActivityLog";

export default function UserDetailClient() {
  const params = useParams();
  const userId = params.id as string;
  const { data: userData, isLoading, isError } = useAdminUserDetailQuery(userId);
  const user = userData?.data;

  if (isLoading) return <div className="text-center p-6">사용자 정보를 불러오는 중...</div>;
  if (isError || !user) return <div className="text-center p-6 text-red-500">사용자 정보를 불러오는 데 실패했습니다.</div>;

  return (
    <div className="space-y-6">
      <div>
        <Button asChild variant="outline" size="sm">
          <Link href="/admin/users"><ArrowLeft className="w-4 h-4 mr-2" /> 목록으로 돌아가기</Link>
        </Button>
        <h2 className="text-2xl font-bold mt-4">사용자 상세 정보: {user.nickname}</h2>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-6">
          <UserInfoCard user={user} />
          {/* 추가적인 통계나 정보 카드를 여기에 넣을 수 있습니다. */}
        </div>
        <div className="lg:col-span-2">
          <UserActivityLog userId={userId} />
        </div>
      </div>
    </div>
  );
}