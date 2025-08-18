// 파일 위치: components/admin/static-page-management.tsx

"use client";

import { useState } from "react";
import { useAdminStaticPagesQuery } from "@/hooks/queries/useAdminStaticPageQueries";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Edit } from "lucide-react";
import { formatDate } from "@/lib/utils/date";
import { EditStaticPageModal } from "@/components/admin/EditStaticPageModal";

export default function StaticPageManagement() {
  const { data: pagesData, isLoading, isError } = useAdminStaticPagesQuery();
  const [editingSlug, setEditingSlug] = useState<string | null>(null);

  const pages = pagesData?.data || [];

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
                  {/* 💡 formatDate에 포맷을 전달하여 시간까지 표시 */}
                  <TableCell>{formatDate(page.updated_at)}</TableCell>
                  <TableCell className="text-right">
                    {/* 💡 2. 수정 버튼 클릭 시 editingSlug 상태를 설정 */}
                    <Button variant="outline" size="sm" onClick={() => setEditingSlug(page.slug)}>
                      <Edit className="h-4 w-4 mr-1" />수정
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* 💡 3. 수정 모달 컴포넌트를 렌더링하고 상태를 전달 */}
      <EditStaticPageModal
        slug={editingSlug}
        onClose={() => setEditingSlug(null)}
      />
    </div>
  );
}