"use client";

import { useState } from 'react';
import { useUpdateUserRoleMutation, useUpdateUserStatusMutation } from '@/hooks/mutations/useAdminUserMutations';
import { formatDate } from "@/lib/utils/date";
import { AdminUserDetail, UserRole, UserStatus } from "@/lib/types/admin/user";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";

const DetailRow = ({ label, value }: { label: string; value: React.ReactNode }) => (
  <div className="flex justify-between items-center text-sm py-2 border-b">
    <span className="text-muted-foreground">{label}</span>
    <span className="font-medium text-right">{value}</span>
  </div>
);

export function UserInfoCard({ user }: { user: AdminUserDetail }) {
  const [modal, setModal] = useState<{ type: 'role' | 'status' | null; newValue: string }>({ type: null, newValue: '' });
  
  const { mutate: updateRole, isPending: isUpdatingRole } = useUpdateUserRoleMutation();
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateUserStatusMutation();

  const handleConfirm = () => {
    if (!modal.type) return;
    if (modal.type === 'role') {
      updateRole({ id: user.user_id, payload: { role: modal.newValue as UserRole } }, { onSuccess: () => setModal({type: null, newValue: ''}) });
    } else {
      updateStatus({ id: user.user_id, payload: { status: modal.newValue as UserStatus } }, { onSuccess: () => setModal({type: null, newValue: ''}) });
    }
  };

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>계정 정보</CardTitle>
          <CardDescription>{user.user_id}</CardDescription>
        </CardHeader>
        <CardContent>
          <DetailRow label="닉네임" value={user.nickname} />
          <DetailRow label="이메일" value={user.email} />
          <DetailRow label="가입일" value={formatDate(user.created_at, 'YYYY-MM-DD HH:mm')} />
          <DetailRow label="최종 수정일" value={formatDate(user.updated_at, 'YYYY-MM-DD HH:mm')} />
          <div className="py-2 space-y-2">
            <div className="flex justify-between items-center text-sm"><span className="text-muted-foreground">역할</span><Select defaultValue={user.role} onValueChange={(v) => setModal({ type: 'role', newValue: v })} disabled={user.role === UserRole.ADMIN}><SelectTrigger className="w-[180px]"><SelectValue /></SelectTrigger><SelectContent>{[UserRole.USER, UserRole.MODERATOR].map(r => <SelectItem key={r} value={r}>{r}</SelectItem>)}</SelectContent></Select></div>
            <div className="flex justify-between items-center text-sm"><span className="text-muted-foreground">상태</span><Select defaultValue={user.status} onValueChange={(v) => setModal({ type: 'status', newValue: v })} disabled={user.role === UserRole.ADMIN}><SelectTrigger className="w-[180px]"><SelectValue /></SelectTrigger><SelectContent>{Object.values(UserStatus).map(s => <SelectItem key={s} value={s}>{s}</SelectItem>)}</SelectContent></Select></div>
          </div>
        </CardContent>
      </Card>
      
      <Dialog open={!!modal.type} onOpenChange={(open) => !open && setModal({ type: null, newValue: '' })}>
        <DialogContent><DialogHeader><DialogTitle>변경 확인</DialogTitle><DialogDescription>정말로 이 사용자의 {modal.type === 'role' ? '역할' : '상태'}을(를) **"{modal.newValue}"**(으)로 변경하시겠습니까?</DialogDescription></DialogHeader><DialogFooter><Button variant="outline" onClick={() => setModal({ type: null, newValue: '' })}>취소</Button><Button onClick={handleConfirm} disabled={isUpdatingRole || isUpdatingStatus}>확인</Button></DialogFooter></DialogContent>
      </Dialog>
    </>
  );
}