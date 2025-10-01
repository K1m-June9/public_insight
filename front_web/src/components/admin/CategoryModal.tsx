
"use client";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { useAdminCategoryDetailQuery } from "@/hooks/queries/useAdminOrganizationQueries";
import { useCreateCategoryMutation, useUpdateCategoryMutation } from "@/hooks/mutations/useAdminOrganizationMutations";
import { AdminSimpleOrganizationItem } from "@/lib/types/admin/organization";

interface CategoryModalProps {
  editingCategory: { id: number } | null;
  organizations: AdminSimpleOrganizationItem[];
  onClose: () => void;
}

export function CategoryModal({ editingCategory, organizations, onClose }: CategoryModalProps) {
  const isEditMode = !!editingCategory;
  const { data: categoryDetailData, isLoading } = useAdminCategoryDetailQuery(editingCategory?.id || null);

  const [formData, setFormData] = useState({ name: '', description: '', organization_id: 0, is_active: true });

  const { mutate: createCategory, isPending: isCreating } = useCreateCategoryMutation();
  const { mutate: updateCategory, isPending: isUpdating } = useUpdateCategoryMutation();

  useEffect(() => {
    if (isEditMode && categoryDetailData?.data) {
      const { name, description, organization_id, is_active } = categoryDetailData.data;
      setFormData({ name, description: description || '', organization_id, is_active });
    } else {
      setFormData({ name: '', description: '', organization_id: 0, is_active: true });
    }
  }, [isEditMode, categoryDetailData]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { ...formData, description: formData.description || null };
    if (isEditMode) {
      updateCategory({ id: editingCategory.id, payload }, { onSuccess: onClose });
    } else {
      createCategory(payload, { onSuccess: onClose });
    }
  };

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditMode ? "카테고리 수정" : "카테고리 생성"}</DialogTitle>
        </DialogHeader>

        {isLoading && isEditMode ? (
          <div>로딩 중...</div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            {/* 기관 선택 */}
            <div>
              <Label htmlFor="organization">기관</Label>
              <Select
                value={formData.organization_id}
                onValueChange={(val) => setFormData({ ...formData, organization_id: Number(val) })}
              >
                <SelectTrigger id="organization">
                  <SelectValue placeholder="기관 선택" />
                </SelectTrigger>
                <SelectContent>
                  {organizations.map((org) => (
                    <SelectItem key={org.id} value={org.id.toString()}>
                      {org.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* 이름 */}
            <div>
              <Label htmlFor="name">카테고리 이름</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            {/* 설명 */}
            <div>
              <Label htmlFor="description">설명</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            {/* 활성화 스위치 */}
            <div className="flex items-center space-x-2">
              <Switch
                checked={formData.is_active}
                onCheckedChange={(checked) => setFormData({ ...formData, is_active: checked })}
              />
              <span>활성화</span>
            </div>

            {/* 버튼 */}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={onClose}>취소</Button>
              <Button type="submit" disabled={isCreating || isUpdating}>{isEditMode ? "수정" : "생성"}</Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
