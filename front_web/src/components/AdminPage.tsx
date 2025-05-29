"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import UserManagement from "./UserManagement"
import CapstoneManagement from "./CapstoneManagement"
import FeedbackManagement from "./FeedbackManagement"
import ReportManagement from "./ReportManagement"

export default function AdminPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">관리자 페이지</h1>
      <Tabs defaultValue="users">
        <TabsList>
          <TabsTrigger value="users">유저 관리</TabsTrigger>
          <TabsTrigger value="capstone">캡스톤 게시물 관리</TabsTrigger>
          <TabsTrigger value="feedback">피드백 관리</TabsTrigger>
          <TabsTrigger value="reports">신고 관리</TabsTrigger>
        </TabsList>
        <TabsContent value="users">
          <UserManagement />
        </TabsContent>
        <TabsContent value="capstone">
          <CapstoneManagement />
        </TabsContent>
        <TabsContent value="feedback">
          <FeedbackManagement />
        </TabsContent>
        <TabsContent value="reports">
          <ReportManagement />
        </TabsContent>
      </Tabs>
    </div>
  )
}

