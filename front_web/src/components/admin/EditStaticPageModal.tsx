"use client";

import { useState, useEffect } from "react";
import { useAdminStaticPageDetailQuery } from "@/hooks/queries/useAdminStaticPageQueries";
import { useUpdateAdminStaticPageMutation } from "@/hooks/mutations/useAdminStaticPageMutations";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";

interface EditStaticPageModalProps {
  slug: string | null;
  onClose: () => void;
}

export function EditStaticPageModal({ slug, onClose }: EditStaticPageModalProps) {
  // 1. slug가 있을 때만 상세 조회 쿼리를 활성화
  const { data: pageDetailData, isLoading: isLoadingDetail } = useAdminStaticPageDetailQuery(slug!, {
    enabled: !!slug,
  });

  // 2. 수정 뮤테이션 훅을 사용
  const { mutate: updatePage, isPending: isSaving } = useUpdateAdminStaticPageMutation();

  const [editContent, setEditContent] = useState("");
  const pageDetail = pageDetailData?.data;

  // 3. 상세 조회 데이터가 로드되면 Textarea의 내용을 업데이트
  useEffect(() => {
    if (pageDetail) {
      setEditContent(pageDetail.content);
    }
  }, [pageDetail]);

  const handleSave = () => {
    if (!slug) return;
    updatePage({ slug, payload: { content: editContent } }, {
      onSuccess: () => {
        onClose(); // 성공 시 모달닫기
      }
    });
  };

  return (
    <Dialog open={!!slug} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-4xl">
        <DialogHeader><DialogTitle>{pageDetail?.title} 콘텐츠 수정</DialogTitle></DialogHeader>
        
        {isLoadingDetail ? (
          <div className="min-h-[400px] flex items-center justify-center">
            콘텐츠를 불러오는 중...
          </div>
        ) : (
          <Textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            className="min-h-[400px] font-mono"
            placeholder="Markdown 형식으로 내용을 입력하세요..."
          />
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button onClick={handleSave} disabled={isSaving || isLoadingDetail}>
            {isSaving ? "저장 중..." : "저장"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}