"use client";

import { useState } from "react";
import { useAdminStaticPagesQuery } from "@/hooks/queries/useAdminStaticPageQueries";
// 💡 관리자용 뮤테이션 훅은 아직 없으므로, 생성 전까지는 수정 기능이 동작하지 않습니다.
// import { useUpdateAdminStaticPageMutation } from "@/hooks/mutations/useAdminStaticPageMutations";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Edit } from "lucide-react";
import { formatDate } from "@/lib/utils/date";
import { AdminStaticPageListItem } from "@/lib/types/admin/staticPage";

export default function StaticPageManagement() {
  // 1. useQuery 훅으로 데이터 가져오기
  const { data: pagesData, isLoading, isError } = useAdminStaticPagesQuery();
  
  // 💡 뮤테이션 훅 (나중에 상세/수정 기능 구현 시 사용)
  // const { mutate: updatePage, isPending: isSaving } = useUpdateAdminStaticPageMutation();

  const [selectedPage, setSelectedPage] = useState<AdminStaticPageListItem | null>(null);
  const [editContent, setEditContent] = useState("");

  const pages = pagesData?.data || [];

  const handleEditClick = (page: AdminStaticPageListItem) => {
    setSelectedPage(page);
    // 💡 상세 조회 API를 호출하여 최신 content를 가져오는 것이 더 좋습니다.
    // 지금은 목록에 있는 content를 그대로 사용합니다.
  };

  const handleSave = () => {
    if (!selectedPage) return;
    // updatePage({ slug: selectedPage.slug, content: editContent });
    console.log("저장 기능은 뮤테이션 훅 구현 후 연결됩니다.");
    setSelectedPage(null); // 임시로 모달 닫기
  };

  if (isLoading) return <div>로딩 중...</div>;
  if (isError) return <div>오류가 발생했습니다.</div>;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>정적 페이지 관리</CardTitle>
          <CardDescription>웹사이트의 주요 정적 페이지(소개, 약관 등)의 내용을 수정합니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>페이지명</TableHead>
                <TableHead>슬러그</TableHead>
                <TableHead>최종 수정일</TableHead>
                <TableHead className="text-right">작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pages.map((page) => (
                <TableRow key={page.id}>
                  <TableCell className="font-medium">{page.title}</TableCell>
                  <TableCell><Badge variant="secondary">/{page.slug}</Badge></TableCell>
                  <TableCell>{formatDate(page.updated_at)}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="outline" size="sm" onClick={() => handleEditClick(page)}>
                      <Edit className="h-4 w-4 mr-1" />수정
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Dialog open={!!selectedPage} onOpenChange={(isOpen) => !isOpen && setSelectedPage(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader><DialogTitle>{selectedPage?.title} 콘텐츠 수정</DialogTitle></DialogHeader>
          <Textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} className="min-h-[400px] font-mono" />
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedPage(null)}>취소</Button>
            <Button onClick={handleSave} /*disabled={isSaving}*/>{/*isSaving ? "저장 중..." :*/ "저장"}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}