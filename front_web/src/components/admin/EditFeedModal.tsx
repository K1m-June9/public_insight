"use client";

import { useState, useEffect } from "react";
import { useAdminFeedDetailQuery } from "@/hooks/queries/useAdminFeedQueries";
import { useUpdateAdminFeedMutation } from "@/hooks/mutations/useAdminFeedMutations";
import { AdminFeedUpdateRequest, ContentType } from "@/lib/types/admin/feed";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";

interface EditFeedModalProps {
  feedId: number | null;
  onClose: () => void;
  organizations: { id: number; name: string }[];
  categories: { id: number; name: string }[];
  onOrganizationChange: (orgId: number) => void;
}

export function EditFeedModal({ feedId, onClose, organizations, categories, onOrganizationChange }: EditFeedModalProps) {
  const { data: feedDetailData, isLoading } = useAdminFeedDetailQuery(feedId, { enabled: !!feedId });
  const { mutate: updateFeed, isPending: isSaving } = useUpdateAdminFeedMutation();

  const [formData, setFormData] = useState<Partial<AdminFeedUpdateRequest>>({});
  const feedDetail = feedDetailData?.data;

  useEffect(() => {
    if (feedDetail) {
      setFormData({
        title: feedDetail.title,
        organization_id: feedDetail.organization_id,
        category_id: feedDetail.category_id,
        summary: feedDetail.summary,
        original_text: feedDetail.original_text,
        source_url: feedDetail.source_url,
        is_active: feedDetail.is_active,
      });
    }
  }, [feedDetail]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSelectChange = (name: keyof AdminFeedUpdateRequest, value: string) => {
    const isNumeric = ['organization_id', 'category_id'].includes(name);
    const parsedValue = isNumeric ? Number(value) : value;
    setFormData(prev => ({ ...prev, [name]: parsedValue }));
    if (name === 'organization_id') {
      onOrganizationChange(parsedValue as number);
      setFormData(prev => ({ ...prev, category_id: undefined })); // 기관 변경 시 카테고리 초기화
    }
  };

  const handleCheckboxChange = (checked: boolean) => {
    setFormData(prev => ({ ...prev, is_active: checked }));
  };

  const handleSave = () => {
    if (!feedId) return;
    updateFeed({ id: feedId, payload: formData as AdminFeedUpdateRequest }, {
      onSuccess: () => onClose(),
    });
  };

  return (
    <Dialog open={!!feedId} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>피드 수정</DialogTitle>
          <DialogDescription>피드 정보를 수정합니다. (NLP 재처리는 수행되지 않습니다)</DialogDescription>
        </DialogHeader>
        {isLoading ? (<div>상세 정보 로딩 중...</div>)
        : feedDetail ? (
          <div className="space-y-4 py-4">
            {/* 폼 필드들 */}
            <div><Label htmlFor="title">제목</Label><Input id="title" name="title" value={formData.title || ''} onChange={handleInputChange} /></div>
            <div className="grid grid-cols-2 gap-4">
              <div><Label htmlFor="organization_id">기관</Label><Select value={String(formData.organization_id || '')} onValueChange={(value) => handleSelectChange('organization_id', value)}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{organizations.map(org => (<SelectItem key={org.id} value={String(org.id)}>{org.name}</SelectItem>))}</SelectContent></Select></div>
              <div><Label htmlFor="category_id">카테고리</Label><Select value={String(formData.category_id || '')} onValueChange={(value) => handleSelectChange('category_id', value)} disabled={!formData.organization_id}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{categories.map(cat => (<SelectItem key={cat.id} value={String(cat.id)}>{cat.name}</SelectItem>))}</SelectContent></Select></div>
            </div>
            <div><Label htmlFor="source_url">원본 URL</Label><Input id="source_url" name="source_url" type="url" value={formData.source_url || ''} onChange={handleInputChange} /></div>
            <div><Label htmlFor="summary">요약문</Label><Textarea id="summary" name="summary" value={formData.summary || ''} onChange={handleInputChange} rows={4} /></div>
            
            {/* content_type에 따른 분기 처리 */}
            {feedDetail.content_type === ContentType.TEXT ? (
              <div><Label htmlFor="original_text">원본 텍스트</Label><Textarea id="original_text" name="original_text" value={formData.original_text || ''} onChange={handleInputChange} rows={6} /></div>
            ) : (
              <div><Label>원본 PDF</Label><div className="text-sm p-2 bg-gray-100 rounded-md"><a href={`${process.env.NEXT_PUBLIC_API_BASE_URL}${feedDetail.pdf_url}`} target="_blank" rel="noopener noreferrer">PDF 원문 보기</a> (PDF 파일 교체는 지원되지 않습니다)</div></div>
            )}

            <div className="flex items-center space-x-2"><Checkbox id="is_active" checked={formData.is_active} onCheckedChange={(checked) => handleCheckboxChange(checked as boolean)} /><Label htmlFor="is_active">활성 상태</Label></div>
          </div>
        ) : (<div>피드 정보를 불러오지 못했습니다.</div>)}
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button onClick={handleSave} disabled={isSaving || isLoading}>수정 완료</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}