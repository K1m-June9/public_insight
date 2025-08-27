import UserDetailClient from '@/components/admin/user-detail-client';

// 💥 params를 더 이상 자식에게 전달하지 않습니다.
export default function AdminUserDetailPage() {
  return (
    <div>
      <UserDetailClient />
    </div>
  );
}