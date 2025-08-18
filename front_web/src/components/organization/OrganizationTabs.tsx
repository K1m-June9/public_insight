"use client";

import { FileText, Newspaper, Users } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import OrganizationFeedList from "./OrganizationFeedList";
import OrganizationPress from "./OrganizationPress";
import OrganizationCommunity from "./OrganizationCommunity";

// 1. 부모(page.tsx)로부터 받을 props 타입을 정의
interface OrganizationTabsProps {
  organizationName: string;
  selectedCategoryId: number | null;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

export default function OrganizationTabs({ 
  organizationName, 
  selectedCategoryId,
  activeTab,
  onTabChange
}: OrganizationTabsProps) {
  return (
    // 2. Tabs 컴포넌트의 value와 onValueChange를 props와 연결합니다.
    <Tabs value={activeTab} onValueChange={onTabChange} className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="policy" className="flex items-center space-x-2">
          <FileText className="w-4 h-4" />
          <span>정책문서</span>
        </TabsTrigger>
        <TabsTrigger value="press" className="flex items-center space-x-2">
          <Newspaper className="w-4 h-4" />
          <span>보도자료</span>
        </TabsTrigger>
        <TabsTrigger value="community" className="flex items-center space-x-2">
          <Users className="w-4 h-4" />
          <span>커뮤니티</span>
        </TabsTrigger>
      </TabsList>
      
      {/* 3. 각 TabsContent 안에 우리가 이전에 만든 컴포넌트들을 배치 */}
      <TabsContent value="policy" className="mt-6">
        <OrganizationFeedList 
          organizationName={organizationName} 
          selectedCategoryId={selectedCategoryId} 
        />
      </TabsContent>
      
      <TabsContent value="press" className="mt-6">
        <OrganizationPress organizationName={organizationName} />
      </TabsContent>
      
      <TabsContent value="community" className="mt-6">
        <OrganizationCommunity organizationName={organizationName} />
      </TabsContent>
    </Tabs>
  );
}