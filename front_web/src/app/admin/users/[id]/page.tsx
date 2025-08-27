import UserDetailClient from '@/components/admin/user-detail-client';

export default function AdminUserDetailPage({ params }: { params: { id: string } }) {
  return (
    <div>
      <UserDetailClient userId={params.id} />
    </div>
  );
}