"use client";

import { useState } from "react";
import { useAdminSlidersQuery } from "@/hooks/queries/useAdminSliderQueries";
import { useUpdateSliderStatusMutation, useDeleteSliderMutation } from "@/hooks/mutations/useAdminSliderMutations";
import { formatDate } from "@/lib/utils/date";
import { AdminSliderListItem } from "@/lib/types/admin/slider";

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Plus, Edit, Trash2, Image as ImageIcon } from "lucide-react";

// Child Components
import { SliderModal } from "@/components/admin/SliderModal";
import { DeleteConfirmModal } from "@/components/admin/DeleteConfirmModal";

export default function SliderManagement() {
  // --- STATE & HOOKS ---
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSlider, setEditingSlider] = useState<AdminSliderListItem | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AdminSliderListItem | null>(null);
  
  const { data: slidersData, isLoading, isError } = useAdminSlidersQuery();
  const { mutate: updateStatus, isPending: isUpdatingStatus } = useUpdateSliderStatusMutation();
  const { mutate: deleteSlider, isPending: isDeleting } = useDeleteSliderMutation();

  const sliders = slidersData?.data || [];

  // --- HANDLERS ---
  const handleEdit = (slider: AdminSliderListItem) => {
    setEditingSlider(slider);
    setIsModalOpen(true);
  };
  
  const handleCreate = () => {
    setEditingSlider(null);
    setIsModalOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (deleteTarget) {
      deleteSlider(deleteTarget.id, {
        onSuccess: () => setDeleteTarget(null)
      });
    }
  };

  const handleToggleActive = (slider: AdminSliderListItem) => {
    updateStatus({ id: slider.id, payload: { is_active: !slider.is_active } });
  };

  // --- RENDER ---
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold">슬라이더 관리</h2>
          <p className="text-muted-foreground">메인 페이지에 표시될 슬라이더를 관리합니다.</p>
        </div>
        <Button onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" /> 새 슬라이더 추가
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>슬라이더 목록</CardTitle>
          <CardDescription>
            표시 순서(오름차순)에 따라 정렬됩니다. 활성화 스위치로 게시 여부를 제어할 수 있습니다.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[80px]">이미지</TableHead>
                <TableHead>제목</TableHead>
                <TableHead className="w-[120px]">태그</TableHead>
                <TableHead className="w-[100px] text-center">표시 순서</TableHead>
                <TableHead className="w-[180px]">게시 기간</TableHead>
                <TableHead className="w-[100px] text-center">활성화</TableHead>
                <TableHead className="text-right w-[160px]">작업</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24">로딩 중...</TableCell></TableRow>
              ) : isError ? (
                <TableRow><TableCell colSpan={7} className="text-center h-24 text-destructive">오류가 발생했습니다.</TableCell></TableRow>
              ) : sliders.map((slider) => (
                <TableRow key={slider.id}>
                  <TableCell>
                    <Avatar className="h-10 w-16 rounded-md">
                      <AvatarImage src={slider.image_path} alt={slider.title} className="object-cover" />
                      <AvatarFallback className="rounded-md"><ImageIcon className="text-muted-foreground" /></AvatarFallback>
                    </Avatar>
                  </TableCell>
                  <TableCell className="font-medium">{slider.title}</TableCell>
                  <TableCell><Badge variant="outline">{slider.tag}</Badge></TableCell>
                  <TableCell className="text-center">{slider.display_order}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(slider.start_date)} ~ {formatDate(slider.end_date)}
                  </TableCell>
                  <TableCell className="text-center">
                    <Switch
                      checked={slider.is_active}
                      onCheckedChange={() => handleToggleActive(slider)}
                      disabled={isUpdatingStatus}
                    />
                  </TableCell>
                  <TableCell className="text-right space-x-2">
                    <Button variant="outline" size="sm" onClick={() => handleEdit(slider)}>
                      <Edit className="w-4 h-4 mr-1" />수정
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => setDeleteTarget(slider)}>
                      <Trash2 className="w-4 h-4 mr-1" />삭제
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      
      {isModalOpen && (
        <SliderModal
          editingSlider={editingSlider}
          onClose={() => setIsModalOpen(false)}
        />
      )}
      
      <DeleteConfirmModal 
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDeleteConfirm}
        targetName={deleteTarget?.title || ''}
        itemType="슬라이더"
        isPending={isDeleting}
      />
    </div>
  );
}