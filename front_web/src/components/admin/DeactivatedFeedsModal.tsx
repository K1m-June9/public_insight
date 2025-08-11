// 파일 위치: front_web/src/components/admin/DeactivatedFeedsModal.tsx

"use client";

import { useState } from "react";
import { useAdminDeactivatedFeedsQuery } from "@/hooks/queries/useAdminFeedQueries";
import { useDeleteAdminFeedMutation } from "@/hooks/mutations/useAdminFeedMutations";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Trash2 } from "lucide-react";
import { formatDate } from "@/lib/utils/date";

interface DeactivatedFeedsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function DeactivatedFeedsModal({ isOpen, onClose }: DeactivatedFeedsModalProps) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useAdminDeactivatedFeedsQuery({ page, limit: 50 });
  const { mutate: deleteFeed, isPending: isDeleting } = useDeleteAdminFeedMutation();

  const feeds = data?.data.feeds || [];
  const pagination = data?.data.pagination;

  const handleDelete = (feedId: number) => {
    if (confirm("이 피드를 완전히 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.")) {
      deleteFeed(feedId);
    }
  };
  
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>비활성화된 피드 관리</DialogTitle>
          <DialogDescription>비활성화된 피드를 확인하고 영구적으로 삭제할 수 있습니다.</DialogDescription>
        </DialogHeader>
        <div className="py-4">
          {isLoading ? (<div>로딩 중...</div>)
          : isError ? (<div className="text-red-500">오류가 발생했습니다.</div>)
          : feeds.length === 0 ? (
            <div className="text-center py-8 text-gray-500">비활성화된 피드가 없습니다.</div>
          ) : (
            <div className="border rounded-lg">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>제목</TableHead>
                    <TableHead>기관</TableHead>
                    <TableHead>카테고리</TableHead>
                    <TableHead>비활성화된 날짜</TableHead>
                    <TableHead className="text-right">작업</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {feeds.map((feed) => (
                    <TableRow key={feed.id}>
                      <TableCell className="font-medium max-w-xs truncate">{feed.title}</TableCell>
                      <TableCell>{feed.organization_name}</TableCell>
                      <TableCell>{feed.category_name}</TableCell>
                      <TableCell>{formatDate(feed.deactivated_at)}</TableCell>
                      <TableCell className="text-right">
                        <Button size="sm" variant="destructive" onClick={() => handleDelete(feed.id)} disabled={isDeleting}>
                          <Trash2 className="h-3 w-3 mr-1" />
                          완전 삭제
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
          {/* 페이지네이션 (추후 구현) */}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>닫기</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}