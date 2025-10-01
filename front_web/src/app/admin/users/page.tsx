import { Suspense } from 'react';
import UserListClient from '@/components/admin/user-list-client';

// URL Search Params를 읽기 위해 Suspense로 감싸줍니다.
export default function AdminUsersPage({
  searchParams,
}: {
  searchParams: { [key: string]: string | string[] | undefined };
}) {
  return (
    <Suspense fallback={<div className="text-center p-10">사용자 목록을 준비 중입니다...</div>}>
      <UserListClient />
    </Suspense>
  );
}