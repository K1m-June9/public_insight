"use client";

import React, { useState, useEffect, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

// Hooks
import { useAdminFeedsListQuery, useAdminOrganizationCategoriesQuery } from "@/hooks/queries/useAdminFeedQueries";
import { useAdminSimpleOrganizationListQuery } from "@/hooks/queries/useAdminOrganizationQueries"; 

// Types
import { AdminFeedListParams, FeedStatus } from "@/lib/types/admin/feed";

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Search, Edit, Trash2, FileText, Clock, CheckCircle, XCircle } from "lucide-react";
import { EditFeedModal } from "@/components/admin/EditFeedModal";
// Utils
import { formatDate } from "@/lib/utils/date";

// URL 쿼리 파라미터를 관리하는 커스텀 훅
function useFeedFilters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const params: AdminFeedListParams = useMemo(() => ({
    page: Number(searchParams.get("page")) || 1,
    limit: 50,
    search: searchParams.get("search") || undefined,
    organization_id: Number(searchParams.get("organization_id")) || undefined,
    category_id: Number(searchParams.get("category_id")) || undefined,
  }), [searchParams]);

  const [localSearch, setLocalSearch] = useState(params.search || "");

  useEffect(() => {
    setLocalSearch(params.search || "");
  }, [params.search]);
  
  const updateFilters = (newFilters: Partial<AdminFeedListParams>) => {
    const current = new URLSearchParams(searchParams.toString());
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        current.set(key, String(value));
      } else {
        current.delete(key);
      }
    });
    if (!('page' in newFilters)) current.set('page', '1');
    
    // 💡 관리자 페이지의 실제 경로로 수정해야 합니다. 예: /admin/feeds
    router.push(`?${current.toString()}`);
  };

  return { params, localSearch, setLocalSearch, updateFilters };
}

// 상태에 따른 뱃지를 렌더링하는 헬퍼 컴포넌트
const StatusBadge = ({ status }: { status: FeedStatus }) => {
    return status === FeedStatus.ACTIVE ? (
      <Badge variant="secondary" className="bg-green-100 text-green-800">활성</Badge>
    ) : (
      <Badge variant="secondary" className="bg-gray-100 text-gray-800">비활성</Badge>
    );
};

// 메인 컴포넌트
export default function FeedManagement() {
  const { params, updateFilters } = useFeedFilters();
  const [localSearch, setLocalSearch] = useState(params.search || "");
  const [editingFeedId, setEditingFeedId] = useState<number | null>(null);
  
  // --- 💡 1. 실제 데이터 페칭으로 교체 ---
  const { data: feedsData, isLoading, isError } = useAdminFeedsListQuery(params);
  const { data: organizationsData } = useAdminSimpleOrganizationListQuery();

  // 수정 모달에서 사용할 기관 ID를 상태로 관리
  const [modalOrganizationId, setModalOrganizationId] = useState<number | null>(null);
  const { data: categoriesData } = useAdminOrganizationCategoriesQuery(modalOrganizationId);
  
  const feeds = feedsData?.data.feeds || [];
  const pagination = feedsData?.data.pagination;
  const organizations = organizationsData?.data || [];
  const categories = categoriesData?.data || [];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    updateFilters({ search: localSearch || undefined });
  };

  const handleEditClick = (feedId: number, orgId: number) => {
    // 수정 모달을 열고, 카테고리 조회를 위해 기관 ID 설정
    setModalOrganizationId(orgId);
    setEditingFeedId(feedId);
  };
  
  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5" />피드 관리</CardTitle>
          <CardDescription>피드를 생성, 수정, 삭제하고 관리할 수 있습니다.</CardDescription>
        </CardHeader>
        <CardContent>
          {/* 검색 및 필터 */}
          <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1 relative"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4" /><Input placeholder="피드 제목으로 검색..." value={localSearch} onChange={(e) => setLocalSearch(e.target.value)} className="pl-10" /></div>
            
            <Select value={String(params.organization_id || '')} onValueChange={(value) => updateFilters({ organization_id: Number(value) || undefined, category_id: undefined })}>
              <SelectTrigger className="w-full md:w-48"><SelectValue placeholder="기관 선택" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">전체 기관</SelectItem>
                {organizations.map((org) => (<SelectItem key={org.id} value={String(org.id)}>{org.name}</SelectItem>))}
              </SelectContent>
            </Select>

            <Select value={String(params.category_id || '')} onValueChange={(value) => updateFilters({ category_id: Number(value) || undefined })} disabled={!params.organization_id}>
              <SelectTrigger className="w-full md:w-48"><SelectValue placeholder="카테고리 선택" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="">전체 카테고리</SelectItem>
                {categories.map((cat) => (<SelectItem key={cat.id} value={String(cat.id)}>{cat.name}</SelectItem>))}
              </SelectContent>
            </Select>
            <Button type="submit">검색</Button>
          </form>

          {/* 액션 버튼 */}
          <div className="flex justify-between items-center mb-6">
             <div className="text-sm text-gray-600">총 {pagination?.total_count || 0}개의 피드</div>
             <div className="flex gap-2">
                <Button variant="outline">{/* <Trash2 className="h-4 w-4 mr-2" /> */}비활성화 관리</Button>
                <Button>{/* <Plus className="h-4 w-4 mr-2" /> */}새 피드 생성</Button>
             </div>
          </div>

          {/* 피드 목록 테이블 */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>제목</TableHead>
                  <TableHead>기관</TableHead>
                  <TableHead>카테고리</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>조회수</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead>작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (<tr><TableCell colSpan={7} className="h-24 text-center">피드 목록을 불러오는 중...</TableCell></tr>)
                : isError ? (<tr><TableCell colSpan={7} className="h-24 text-center text-red-500">오류가 발생했습니다.</TableCell></tr>)
                : feeds.length === 0 ? (<tr><TableCell colSpan={7} className="h-24 text-center">표시할 피드가 없습니다.</TableCell></tr>)
                : feeds.map((feed) => (
                    <TableRow key={feed.id}>
                        <TableCell className="font-medium max-w-xs truncate">{feed.title}</TableCell>
                        <TableCell>{feed.organization_name}</TableCell>
                        <TableCell>{feed.category_name}</TableCell>
                        <TableCell><StatusBadge status={feed.status} /></TableCell>
                        <TableCell>{feed.view_count.toLocaleString()}</TableCell>
                        <TableCell>{formatDate(feed.created_at)}</TableCell>
                        <TableCell>
                          {/* 💡 수정 버튼 클릭 시 handleEditClick 호출 */}
                          <Button size="sm" variant="outline" onClick={() => handleEditClick(feed.id, feed.organization_id)}>
                            <Edit className="h-3 w-3" />
                          </Button>
                        </TableCell>
                    </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* 페이지네이션 */}
          {pagination && pagination.total_pages > 1 && (
            <div className="flex justify-center items-center gap-2 mt-6">
                <Button variant="outline" size="sm" onClick={() => updateFilters({ page: pagination.current_page - 1 })} disabled={!pagination.has_previous}>이전</Button>
                <span className="text-sm text-gray-600">{pagination.current_page} / {pagination.total_pages}</span>
                <Button variant="outline" size="sm" onClick={() => updateFilters({ page: pagination.current_page + 1 })} disabled={!pagination.has_next}>다음</Button>
            </div>
          )}
        </CardContent>
      </Card>
      {/* 💡 수정 모달 컴포넌트 렌더링 */}
      <EditFeedModal
        feedId={editingFeedId}
        onClose={() => setEditingFeedId(null)}
        organizations={organizations}
        categories={categories}
        onOrganizationChange={setModalOrganizationId}
      />
      
      {/* 생성/수정/비활성화 모달은 다음 단계에서 구현 */}
    </div>
  );
}