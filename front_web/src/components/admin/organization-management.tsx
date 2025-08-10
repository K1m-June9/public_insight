"use client";

import React, {useState} from "react";
import { useAdminOrganizationsListQuery, useAdminSimpleOrganizationListQuery } from "@/hooks/queries/useAdminOrganizationQueries";
import { useDeleteOrganizationMutation, useDeleteCategoryMutation } from "@/hooks/mutations/useAdminOrganizationMutations";

// UI Components
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ChevronDown, ChevronRight, Plus, Edit, Trash2, Building2, FolderOpen } from "lucide-react";
import { OrganizationModal } from "@/components/admin/OrganizationModal";
import { CategoryModal } from "@/components/admin/CategoryModal";
import { DeleteConfirmModal } from "@/components/admin/DeleteConfirmModal";

// Types
import { AdminOrganizationWithCategories, AdminCategoryItem } from "@/lib/types/admin/organization";

export default function OrganizationManagement() {
  const { data: orgData, isLoading, isError } = useAdminOrganizationsListQuery();
  const { data: simpleOrgsData } = useAdminSimpleOrganizationListQuery(); // 모달 전달용
  
  // 모달 상태 관리
  const [modalState, setModalState] = useState<{ type: 'org' | 'cat' | null; data: any | null }>({ type: null, data: null });
  const [deleteTarget, setDeleteTarget] = useState<{ type: "org" | "category"; id: number; name: string } | null>(null);
  const [expandedOrgs, setExpandedOrgs] = useState<Set<number>>(new Set());

  // 뮤테이션 훅
  const { mutate: deleteOrg, isPending: isDeletingOrg } = useDeleteOrganizationMutation();
  const { mutate: deleteCat, isPending: isDeletingCat } = useDeleteCategoryMutation();

  const organizations = orgData?.data || [];
  const simpleOrganizations = simpleOrgsData?.data || [];

  const toggleOrganization = (orgId: number) => {
    const newExpanded = new Set(expandedOrgs);
    if (newExpanded.has(orgId)) newExpanded.delete(orgId);
    else newExpanded.add(orgId);
    setExpandedOrgs(newExpanded);
  };
  
  const handleDelete = () => {
    if (!deleteTarget) return;
    const action = deleteTarget.type === 'org' ? deleteOrg : deleteCat;
    action(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) });
  };

  const renderContent = () => {
    if (isLoading) return <div className="text-center p-6">기관 목록을 불러오는 중...</div>;
    if (isError) return <div className="text-center p-6 text-red-500">데이터를 불러오는 중 오류가 발생했습니다.</div>;
    if (organizations.length === 0) return <div className="text-center p-6 text-gray-500">등록된 기관이 없습니다.</div>;

    return (
      <div className="space-y-4">
        {organizations.map((org: AdminOrganizationWithCategories) => (
          <div key={org.id} className="border rounded-lg">
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
                <Button variant="outline" size="sm" onClick={() => setModalState({ type: 'org', data: org })}>
                  <Edit className="w-4 h-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => setDeleteTarget({ type: 'org', id: org.id, name: org.name })}>
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
            {expandedOrgs.has(org.id) && (
              <div className="p-4 space-y-2">
                {org.categories.map((category: AdminCategoryItem) => (
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
                      <Button variant="outline" size="sm" onClick={() => setModalState({ type: 'cat', data: category })}>
                        <Edit className="w-4 h-4" />
                      </Button>
                      {category.name !== "보도자료" && (
                        <Button variant="outline" size="sm" onClick={() => setDeleteTarget({ type: 'category', id: category.id, name: category.name })}>
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      )}
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
          <Button onClick={() => setModalState({ type: 'org', data: null })}><Plus className="w-4 h-4 mr-2" />기관 추가</Button>
          <Button variant="outline" onClick={() => setModalState({ type: 'cat', data: null })}><Plus className="w-4 h-4 mr-2" />카테고리 추가</Button>
        </div>
      </div>
      <Card>
        <CardContent className="p-6">
          {renderContent()}
        </CardContent>
      </Card>

      {modalState.type === 'org' && <OrganizationModal editingOrg={modalState.data} onClose={() => setModalState({ type: null, data: null })} />}
      {modalState.type === 'cat' && <CategoryModal editingCategory={modalState.data} organizations={simpleOrganizations} onClose={() => setModalState({ type: null, data: null })} />}
      <DeleteConfirmModal 
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={handleDelete}
        targetName={deleteTarget?.name || ''}
        itemType={deleteTarget?.type === 'org' ? '기관' : '카테고리'}
        isPending={isDeletingOrg || isDeletingCat}
      />
    </div>
  );
}