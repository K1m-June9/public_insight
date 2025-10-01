"use client";

import { useState, useEffect } from "react";
import { useAdminSliderDetailQuery } from "@/hooks/queries/useAdminSliderQueries";
import { useCreateSliderMutation, useUpdateSliderMutation } from "@/hooks/mutations/useAdminSliderMutations";
import { formatDate } from "@/lib/utils/date";

// UI Components
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Image as ImageIcon } from "lucide-react";

// Types
import { AdminSliderListItem, AdminSliderFormRequest } from "@/lib/types/admin/slider";

interface SliderModalProps {
  editingSlider: AdminSliderListItem | null;
  onClose: () => void;
}

const INITIAL_FORM_STATE: AdminSliderFormRequest = {
  title: "",
  preview: "",
  tag: "",
  content: "",
  display_order: 0,
  start_date: null,
  end_date: null,
};

export function SliderModal({ editingSlider, onClose }: SliderModalProps) {
  const isEditMode = !!editingSlider;
  
  const { data: sliderDetailData, isLoading: isLoadingDetail } = useAdminSliderDetailQuery(editingSlider?.id || null);
  
  const [formData, setFormData] = useState<AdminSliderFormRequest>(INITIAL_FORM_STATE);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  
  const { mutate: createSlider, isPending: isCreating } = useCreateSliderMutation();
  const { mutate: updateSlider, isPending: isUpdating } = useUpdateSliderMutation();

  useEffect(() => {
    if (isEditMode && sliderDetailData?.data) {
      const { title, preview, tag, content, display_order, start_date, end_date, image_url } = sliderDetailData.data;
      setFormData({ 
        title, 
        preview, 
        tag, 
        content, 
        display_order, 
        start_date: formatDate(start_date), 
        end_date: formatDate(end_date) 
      });
      setImagePreview(image_url);
    }
  }, [isEditMode, sliderDetailData]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'number' ? parseInt(value) || 0 : value }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const submissionData = new FormData();
    Object.entries(formData).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        submissionData.append(key, String(value));
      }
    });
    if (imageFile) {
      submissionData.append('image', imageFile);
    }
    
    if (isEditMode) {
      updateSlider({ id: editingSlider.id, formData: submissionData }, { onSuccess: onClose });
    } else {
      createSlider(submissionData, { onSuccess: onClose });
    }
  };

  const isPending = isCreating || isUpdating;

  return (
    <Dialog open={true} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-4xl">
        <DialogHeader>
          <DialogTitle>{isEditMode ? "슬라이더 수정" : "새 슬라이더 생성"}</DialogTitle>
          <DialogDescription>슬라이더에 표시될 내용을 입력하고 이미지를 업로드하세요.</DialogDescription>
        </DialogHeader>
        
        {isLoadingDetail && isEditMode ? (
          <div className="min-h-[400px] flex items-center justify-center">로딩 중...</div>
        ) : (
          <form id="slider-form" onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-6 py-4">
            <div className="md:col-span-1 space-y-2">
              <Label>이미지</Label>
              <Avatar className="h-32 w-full rounded-lg">
                <AvatarImage src={imagePreview || ''} alt="슬라이더 이미지 미리보기" className="object-cover" />
                <AvatarFallback className="rounded-lg bg-muted"><ImageIcon className="h-8 w-8 text-muted-foreground" /></AvatarFallback>
              </Avatar>
              <Input type="file" accept="image/*" onChange={handleImageChange} />
              <p className="text-xs text-muted-foreground">권장 사이즈: 1200x400px</p>
            </div>
            
            <div className="md:col-span-2 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div><Label htmlFor="title">제목 *</Label><Input id="title" name="title" value={formData.title} onChange={handleInputChange} required /></div>
                <div><Label htmlFor="tag">태그 *</Label><Input id="tag" name="tag" value={formData.tag} onChange={handleInputChange} required /></div>
              </div>
              <div><Label htmlFor="preview">미리보기 문구 *</Label><Input id="preview" name="preview" value={formData.preview} onChange={handleInputChange} required /></div>
              <div><Label htmlFor="content">내용 (Markdown) *</Label><Textarea id="content" name="content" value={formData.content} onChange={handleInputChange} rows={6} required /></div>
              <div className="grid grid-cols-3 gap-4">
                <div><Label htmlFor="display_order">표시 순서</Label><Input id="display_order" name="display_order" type="number" value={formData.display_order} onChange={handleInputChange} /></div>
                <div><Label htmlFor="start_date">게시 시작일</Label><Input id="start_date" name="start_date" type="date" value={formData.start_date || ''} onChange={handleInputChange} /></div>
                <div><Label htmlFor="end_date">게시 종료일</Label><Input id="end_date" name="end_date" type="date" value={formData.end_date || ''} onChange={handleInputChange} /></div>
              </div>
            </div>
          </form>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button type="submit" form="slider-form" disabled={isPending || isLoadingDetail}>
            {isPending ? "저장 중..." : (isEditMode ? "수정 완료" : "생성 완료")}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}