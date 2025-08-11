"use client";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { AlertTriangle } from "lucide-react";

interface DeleteConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  targetName: string;
  itemType: '기관' | '카테고리';
  isPending: boolean;
}

export function DeleteConfirmModal({ isOpen, onClose, onConfirm, targetName, itemType, isPending }: DeleteConfirmModalProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader><DialogTitle className="flex items-center gap-2"><AlertTriangle className="text-red-500" />삭제 확인</DialogTitle></DialogHeader>
        <div className="py-4">
          <p>정말로 **"{targetName}"** {itemType}을(를) 삭제하시겠습니까?</p>
          <p className="text-sm text-red-600 mt-2">이 작업은 되돌릴 수 없습니다.</p>
        </div>
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button variant="destructive" onClick={onConfirm} disabled={isPending}>{isPending ? "삭제 중..." : "삭제"}</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}