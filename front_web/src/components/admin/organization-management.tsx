// 파일 위치: components/admin/organization-management.tsx

"use client";

import React, { useState } from "react";
// 💡 Hooks
import { useAdminOrganizationsListQuery } from "@/hooks/queries/useAdminOrganizationQueries";

// 💡 UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, Plus, Edit, Trash2, Building2, FolderOpen } from "lucide-react";
// ... (향후 사용할 모달 관련 컴포넌트들)

// 💡 Types
import { AdminOrganizationWithCategories } from "@/lib/types/admin/organization";


export default function OrganizationManagement() {
  // 1. 실제 데이터 로딩을 위한 훅 호출
  const { data: orgData, isLoading, isError } = useAdminOrganizationsListQuery();
  const organizations = orgData?.data || [];
  
  const [expandedOrgs, setExpandedOrgs] = useState<Set<number>>(new Set());

  // 모달 관련 상태 (다음 기능 개발 시 사용)
  const [orgModalOpen, setOrgModalOpen] = useState(false);
  const [categoryModalOpen, setCategoryModalOpen] = useState(false);

  // 기관 토글 함수
  const toggleOrganization = (orgId: number) => {
    const newExpanded = new Set(expandedOrgs);
    if (newExpanded.has(orgId)) {
      newExpanded.delete(orgId);
    } else {
      newExpanded.add(orgId);
    }
    setExpandedOrgs(newExpanded);
  };

  const renderContent = () => {
    if (isLoading) {
      return <div className="text-center p-6">기관 목록을 불러오는 중...</div>;
    }
    if (isError) {
      return <div className="text-center p-6 text-red-500">데이터를 불러오는 중 오류가 발생했습니다.</div>;
    }
    if (organizations.length === 0) {
      return <div className="text-center p-6 text-gray-500">등록된 기관이 없습니다.</div>;
    }

    return (
      <div className="space-y-4">
        {organizations.map((org: AdminOrganizationWithCategories) => (
          <div key={org.id} className="border rounded-lg">
            {/* 기관 헤더 */}
            <div className="p-4 bg-gray-50 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Button variant="ghost" size="sm" onClick={() => toggleOrganization(org.id)}>
                  {expandedOrgs.has(org.id) ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                </Button>
                <div>
                  <div className="flex items-center space-x-2">
                    <Building2 className="w-4 h-4" />
                    <span className="font-medium">{org.name}</span>
                    <Badge variant={org.is_active ? "default" : "secondary"}>{org.is_active ? "활성" : "비활성"}</Badge>
                    <Badge variant="outline">피드 {org.feed_count}개</Badge>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">{/* <Edit className="w-4 h-4" /> */ "수정"}</Button>
                <Button variant="outline" size="sm">{/* <Trash2 className="w-4 h-4" /> */ "삭제"}</Button>
              </div>
            </div>
            {/* 카테고리 목록 */}
            {expandedOrgs.has(org.id) && (
              <div className="p-4 space-y-2">
                {org.categories.map((category) => (
                  <div key={category.id} className="flex items-center justify-between p-3 bg-white border rounded">
                    <div className="flex items-center space-x-3">
                      <FolderOpen className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium">{category.name}</span>
                          <Badge variant={category.is_active ? "default" : "secondary"}>{category.is_active ? "활성" : "비활성"}</Badge>
                          <Badge variant="outline">피드 {category.feed_count}개</Badge>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">{/* <Edit className="w-4 h-4" /> */ "수정"}</Button>
                      {category.name !== "보도자료" && <Button variant="outline" size="sm">{/* <Trash2 className="w-4 h-4" /> */ "삭제"}</Button>}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">기관/카테고리 관리</h2>
        <div className="space-x-2">
          <Button>{/* <Plus className="w-4 h-4 mr-2" /> */}기관 추가</Button>
          <Button variant="outline">{/* <Plus className="w-4 h-4 mr-2" /> */}카테고리 추가</Button>
        </div>
      </div>
      <Card>
        <CardContent className="p-6">
          {renderContent()}
        </CardContent>
      </Card>
      
      {/* TODO: 생성/수정/삭제 모달 */}
    </div>
  );
}