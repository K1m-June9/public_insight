"use client";

import { useState } from "react";
import { useAdminNoticesQuery } from "@/hooks/queries/useAdminNoticeQueries";
import { useUpdateNoticeStatusMutation, useDeleteNoticeMutation } from "@/hooks/mutations/useAdminNoticeMutations";
import { formatDate } from "@/lib/utils/date";
import { AdminNoticeListItem } from "@/lib/types/admin/notice";

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Plus, Edit, Trash2, Pin, PinOff } from "lucide-react";

// Child Components
import { NoticeModal } from "@/components/admin/NoticeModal";
import { DeleteConfirmModal } from "@/components/admin/DeleteConfirmModal";

export default function NoticeManagement() {
  // --- STATE & HOOKS ---
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingNotice, setEditingNotice] = useState<AdminNoticeListItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminNoticeListItem | null>(null);
  
  const { data: noticesData, isLoading, isError } = useAdminNoticesQuery();
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateNoticeStatusMutation();
  const { mutate: deleteNotice, isPending: isDeleting } = useDeleteNoticeMutation();

  const notices = noticesData?.data || [];

  // --- HANDLERS ---
  const handleEdit = (notice: AdminNoticeListItem) => {
    setEditingNotice(notice);
    setIsModalOpen(true);
  };
  
  const handleCreate = () => {
    setEditingNotice(null);
    setIsModalOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteTarget) {
      deleteNotice(deleteTarget.id, {
        onSuccess: () => setDeleteTarget(null)
      });
    }
  };

  const handleTogglePin = (notice: AdminNoticeListItem) => {
    updateStatus({ id: notice.id, payload: { is_pinned: !notice.is_pinned } });
  };

  const handleToggleActive = (notice: AdminNoticeListItem) => {
    updateStatus({ id: notice.id, payload: { is_active: !notice.is_active } });
  };

  // --- RENDER ---
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">공지사항 관리</h2>
          <p className="text-muted-foreground">웹사이트에 게시될 공지사항을 관리합니다.</p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" /> 새 공지사항 작성
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>공지사항 목록</CardTitle>
          <CardDescription>
            고정된 공지사항이 최상단에 표시됩니다. 활성화 스위치를 통해 게시 여부를 제어할 수 있습니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[80px] text-center">고정</TableHead>
                <TableHead>제목</TableHead>
                <TableHead className="w-[120px]">작성자</TableHead>
                <TableHead className="w-[100px] text-center">조회수</TableHead>
                <TableHead className="w-[180px]">최종 수정일</TableHead>
                <TableHead className="w-[100px] text-center">활성화</TableHead>
                <TableHead className="text-right w-[160px]">작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24">로딩 중...</TableCell></TableRow>
              ) : isError ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24 text-destructive">오류가 발생했습니다.</TableCell></TableRow>
              ) : notices.map((notice) => (
                <TableRow key={notice.id} className={notice.is_pinned ? "bg-secondary" : ""}>
                  <TableCell className="text-center">
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Button variant="ghost" size="icon" onClick={() => handleTogglePin(notice)} disabled={isUpdatingStatus}>
                            {notice.is_pinned ? <Pin className="w-4 h-4 text-primary" /> : <PinOff className="w-4 h-4 text-muted-foreground" />}
                          </Button>
                        </TooltipTrigger>
                        <TooltipContent>{notice.is_pinned ? "고정 해제" : "고정하기"}</TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </TableCell>
                  <TableCell className="font-medium">{notice.title}</TableCell>
                  <TableCell>{notice.author}</TableCell>
                  <TableCell className="text-center">{notice.view_count}</TableCell>
                  <TableCell>{formatDate(notice.updated_at)}</TableCell>
                  <TableCell className="text-center">
                    <Switch
                      checked={notice.is_active}
                      onCheckedChange={() => handleToggleActive(notice)}
                      disabled={isUpdatingStatus}
                    />
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => handleEdit(notice)}>
                      <Edit className="w-4 h-4 mr-1" />수정
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setDeleteTarget(notice)} disabled={notice.is_pinned}>
                      <Trash2 className="w-4 h-4 mr-1" />삭제
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {/* --- MODALS --- */}
      {isModalOpen && (
        <NoticeModal
          editingNotice={editingNotice}
          onClose={() => setIsModalOpen(false)}
        />
      )}
      
      <DeleteConfirmModal 
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        targetName={deleteTarget?.title || ''}
        itemType="공지사항"
        isPending={isDeleting}
      />
    </div>
  );
}