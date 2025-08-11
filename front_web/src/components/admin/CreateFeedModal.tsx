// 파일 위치: front_web/src/components/admin/CreateFeedModal.tsx

"use client";

import { useState } from "react";
import { useCreateAdminFeedMutation } from "@/hooks/mutations/useAdminFeedMutations";
import { useAdminSimpleOrganizationListQuery } from "@/hooks/queries/useAdminOrganizationQueries";
import { useAdminOrganizationCategoriesQuery } from "@/hooks/queries/useAdminFeedQueries";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Upload } from "lucide-react";

interface CreateFeedModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const INITIAL_FORM_STATE = {
  title: "",
  organization_id: "",
  category_id: "",
  source_url: "",
  published_date: "",
  content_type: "text",
  original_text: "",
  pdf_file: null as File | null,
};

export function CreateFeedModal({ isOpen, onClose }: CreateFeedModalProps) {
  const { mutate: createFeed, isPending } = useCreateAdminFeedMutation();
  const [formData, setFormData] = useState(INITIAL_FORM_STATE);

  const { data: organizationsData } = useAdminSimpleOrganizationListQuery();
  const { data: categoriesData } = useAdminOrganizationCategoriesQuery(Number(formData.organization_id) || null);

  const organizations = organizationsData?.data || [];
  const categories = categoriesData?.data || [];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSelectChange = (name: 'organization_id' | 'category_id', value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (name === 'organization_id') {
      setFormData(prev => ({ ...prev, category_id: "" })); // 기관 변경 시 카테고리 초기화
    }
  };

  const handleSubmit = () => {
    // 1. FormData 객체 생성
    const submissionData = new FormData();
    
    // 2. 각 필드를 FormData에 추가
    submissionData.append('title', formData.title);
    submissionData.append('organization_id', formData.organization_id);
    submissionData.append('category_id', formData.category_id);
    submissionData.append('source_url', formData.source_url);
    submissionData.append('published_date', formData.published_date);
    submissionData.append('content_type', formData.content_type);
    
    if (formData.content_type === 'text') {
      submissionData.append('original_text', formData.original_text);
    } else if (formData.pdf_file) {
      submissionData.append('pdf_file', formData.pdf_file);
    }

    // 3. 뮤테이션 훅 호출
    createFeed(submissionData, {
      onSuccess: () => {
        setFormData(INITIAL_FORM_STATE); // 폼 초기화
        onClose(); // 모달 닫기
      },
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>새 피드 생성</DialogTitle>
          <DialogDescription>새로운 피드를 생성합니다. 처리 완료까지 시간이 소요될 수 있습니다.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div><Label htmlFor="title">제목 *</Label><Input id="title" name="title" value={formData.title} onChange={handleInputChange} /></div>
          <div className="grid grid-cols-2 gap-4">
            <div>
            <Label htmlFor="organization_id">기관 *</Label>
            <Select value={formData.organization_id} onValueChange={(value) => handleSelectChange('organization_id', value)}>
              <SelectTrigger>
                <SelectValue placeholder="기관 선택" />
              </SelectTrigger>
              <SelectContent>
                {organizations.map(org => (<SelectItem key={org.id} value={String(org.id)}>{org.name}</SelectItem>))}
              </SelectContent>
            </Select>
            </div>
            <div>
              <Label htmlFor="category_id">카테고리 *</Label>
              <Select value={formData.category_id} onValueChange={(value) => handleSelectChange('category_id', value)} disabled={!formData.organization_id}>
                <SelectTrigger><SelectValue placeholder="카테고리 선택" /></SelectTrigger>
                <SelectContent>{categories.map(cat => (<SelectItem key={cat.id} value={String(cat.id)}>{cat.name}</SelectItem>))}</SelectContent>
              </Select>
              </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="source_url">원본 URL *</Label>
              <Input id="source_url" name="source_url" type="url" value={formData.source_url} onChange={handleInputChange} />
            </div>
            <div>
              <Label htmlFor="published_date">발행 일시 *</Label>
              <Input id="published_date" name="published_date" type="date" value={formData.published_date} onChange={handleInputChange} />
            </div>
          </div>
          <div>
            <Label>콘텐츠 유형 *</Label>
            <Tabs value={formData.content_type} onValueChange={(value) => setFormData({ ...formData, content_type: value })}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="text">텍스트 입력</TabsTrigger>
                <TabsTrigger value="pdf">PDF 업로드</TabsTrigger>
              </TabsList>
              <TabsContent value="text" className="mt-4"><Label htmlFor="original_text">원본 텍스트 *</Label>
              <Textarea id="original_text" name="original_text" value={formData.original_text} onChange={handleInputChange} rows={6} />
              </TabsContent>
              <TabsContent value="pdf" className="mt-4">
                <Label htmlFor="pdf_file">PDF 파일 *</Label>
                <Input id="pdf_file" type="file" accept=".pdf" onChange={(e) => setFormData({ ...formData, pdf_file: e.target.files?.[0] || null })} />
                </TabsContent>
            </Tabs>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>취소</Button>
          <Button onClick={handleSubmit} disabled={isPending}><Upload className="h-4 w-4 mr-2" />{isPending ? "요청 중..." : "생성 요청"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}