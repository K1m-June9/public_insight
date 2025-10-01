"use client";

import { useState, useEffect } from "react";
import { useAdminOrganizationDetailQuery } from "@/hooks/queries/useAdminOrganizationQueries";
import { useCreateOrganizationMutation, useUpdateOrganizationMutation } from "@/hooks/mutations/useAdminOrganizationMutations";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { AdminOrganizationDetail, AdminOrganizationRequest } from "@/lib/types/admin/organization";

interface OrganizationModalProps {
  editingOrg: AdminOrganizationDetail | null;
  onClose: () => void;
}

const INITIAL_FORM_STATE = {
  name: "",
  description: "",
  website_url: "",
  is_active: true,
};

export function OrganizationModal({ editingOrg, onClose }: OrganizationModalProps) {
  const isEditMode = !!editingOrg;
  const { data: orgDetailData, isLoading } = useAdminOrganizationDetailQuery(editingOrg?.id || null);

  const [formData, setFormData] = useState<Omit<AdminOrganizationRequest, 'icon'>>(INITIAL_FORM_STATE);

  const { mutate: createOrg, isPending: isCreating } = useCreateOrganizationMutation();
  const { mutate: updateOrg, isPending: isUpdating } = useUpdateOrganizationMutation();

  useEffect(() => {
    if (isEditMode && orgDetailData?.data) {
      const { name, description, website_url, is_active } = orgDetailData.data;
      setFormData({ name, description: description || '', website_url: website_url || '', is_active });
    } else {
      setFormData(INITIAL_FORM_STATE);
    }
  }, [isEditMode, orgDetailData]);
  
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      
      // formData state 객체를 직접 payload로 사용
      const payload: AdminOrganizationRequest = {
          name: formData.name,
          description: formData.description || null,
          website_url: formData.website_url || null,
          is_active: formData.is_active,
      };

      if (isEditMode) {
          updateOrg({ id: editingOrg.id, payload }, { onSuccess: onClose });
      } else {
          // 생성 API도 JSON을 받도록 수정했으므로, payload를 그대로 전달
          createOrg(payload, { onSuccess: onClose });
      }
  };

  return (
    <Dialog open={true} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader><DialogTitle>{isEditMode ? "기관 수정" : "기관 생성"}</DialogTitle></DialogHeader>
        {isLoading && isEditMode ? (<div>로딩 중...</div>) : (
          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            <div><Label htmlFor="name">기관명 *</Label><Input id="name" name="name" value={formData.name} onChange={handleInputChange} required /></div>
            <div>
              <Label htmlFor="description">기관 설명</Label>
              <Textarea id="description" name="description" value={formData.description ?? ''} onChange={handleInputChange} rows={3} />
            </div>
            <div>
              <Label htmlFor="website_url">웹사이트 URL</Label>
              <Input id="website_url" name="website_url" type="url" value={formData.website_url ?? ''} onChange={handleInputChange} />
            </div>
            <div className="flex items-center space-x-2"><Switch id="is_active" checked={formData.is_active} onCheckedChange={(checked) => setFormData(prev => ({ ...prev, is_active: checked }))} /><Label htmlFor="is_active">활성화</Label></div>
            <div className="flex justify-end space-x-2 pt-4">
              <Button type="button" variant="outline" onClick={onClose}>취소</Button>
              <Button type="submit" disabled={isCreating || isUpdating}>{isEditMode ? "수정" : "생성"}</Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}