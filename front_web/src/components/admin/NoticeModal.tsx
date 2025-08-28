"use client";

import { useState, useEffect } from "react";
import { useAdminNoticeDetailQuery } from "@/hooks/queries/useAdminNoticeQueries";
import { useCreateNoticeMutation, useUpdateNoticeMutation } from "@/hooks/mutations/useAdminNoticeMutations";

// UI Components
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";

// Types
import { AdminNoticeListItem, AdminNoticeCreateRequest, AdminNoticeUpdateRequest } from "@/lib/types/admin/notice";

interface NoticeModalProps {
  editingNotice: AdminNoticeListItem | null;
  onClose: () => void;
}

const INITIAL_FORM_STATE = {
  title: "",
  content: "",
  is_active: true,
};

export function NoticeModal({ editingNotice, onClose }: NoticeModalProps) {
  const isEditMode = !!editingNotice;
  
  // 수정 모드일 때만 상세 데이터를 불러옵니다.
  const { data: noticeDetailData, isLoading: isLoadingDetail } = useAdminNoticeDetailQuery(editingNotice?.id || null);
  
  const [formData, setFormData] = useState<AdminNoticeCreateRequest | AdminNoticeUpdateRequest>(INITIAL_FORM_STATE);
  
  const { mutate: createNotice, isPending: isCreating } = useCreateNoticeMutation();
  const { mutate: updateNotice, isPending: isUpdating } = useUpdateNoticeMutation();

  // 수정 모드이고, 상세 데이터 로딩이 끝나면 폼을 채웁니다.
  useEffect(() => {
    if (isEditMode && noticeDetailData?.data) {
      const { title, content, is_active } = noticeDetailData.data;
      setFormData({ title, content, is_active });
    }
  }, [isEditMode, noticeDetailData]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isEditMode) {
      updateNotice({ id: editingNotice.id, payload: formData as AdminNoticeUpdateRequest }, { onSuccess: onClose });
    } else {
      createNotice(formData as AdminNoticeCreateRequest, { onSuccess: onClose });
    }
  };

  const isPending = isCreating || isUpdating;

  return (
    <Dialog open={true} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>{isEditMode ? "공지사항 수정" : "새 공지사항 작성"}</DialogTitle>
        </DialogHeader>
        
        {isLoadingDetail && isEditMode ? (
          <div className="min-h-[400px] flex items-center justify-center">
            공지사항 내용을 불러오는 중...
          </div>
        ) : (
          <form id="notice-form" onSubmit={handleSubmit} className="space-y-4 py-4">
            <div>
              <Label htmlFor="title">제목 *</Label>
              <Input id="title" name="title" value={formData.title} onChange={handleInputChange} required />
            </div>
            <div>
              <Label htmlFor="content">내용 *</Label>
              <Textarea id="content" name="content" value={formData.content} onChange={handleInputChange} rows={12} required />
            </div>
            <div className="flex items-center space-x-2">
              <Switch id="is_active" checked={formData.is_active} onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))} />
              <Label htmlFor="is_active">게시 활성화</Label>
            </div>
          </form>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button type="submit" form="notice-form" disabled={isPending || isLoadingDetail}>
            {isPending ? "저장 중..." : (isEditMode ? "수정 완료" : "작성 완료")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}