"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

type Feedback = {
  id: string
  userId: string
  type: string
  content: string
  createdAt: string
}

const feedbackTypes = [
  { value: "1", label: "사용성" },
  { value: "2", label: "요약 퀄리티" },
  { value: "3", label: "정보의 정확성" },
  { value: "4", label: "UI/UX" },
  { value: "5", label: "기능 제안" },
]

const mockFeedback: Feedback[] = [
  { id: "1", userId: "user1", type: "1", content: "네비게이션이 직관적이지 않음", createdAt: "2024-03-15" },
  {
    id: "2",
    userId: "user2",
    type: "2",
    content: "요약이 너무 길고 핵심을 놓치는 경우가 있음",
    createdAt: "2024-03-16",
  },
  { id: "3", userId: "user3", type: "3", content: "일부 정책 정보가 최신 내용이 아님", createdAt: "2024-03-17" },
  { id: "4", userId: "user4", type: "4", content: "모바일에서 가독성이 떨어짐", createdAt: "2024-03-18" },
  { id: "5", userId: "user5", type: "5", content: "개인화된 알림 기능 추가 요청", createdAt: "2024-03-19" },
]

export default function FeedbackManagement() {
  const [selectedType, setSelectedType] = useState<string | undefined>()

  const filteredFeedback = selectedType
    ? mockFeedback.filter((feedback) => feedback.type === selectedType)
    : mockFeedback

  return (
    <Card>
      <CardHeader>
        <CardTitle>피드백 관리</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Select onValueChange={setSelectedType}>
            <SelectTrigger>
              <SelectValue placeholder="피드백 유형 선택" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">전체</SelectItem>
              {feedbackTypes.map((type) => (
                <SelectItem key={type.value} value={type.value}>
                  {type.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>유형</TableHead>
              <TableHead>내용</TableHead>
              <TableHead>제출일</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredFeedback.map((feedback) => (
              <TableRow key={feedback.id}>
                <TableCell>{feedback.userId}</TableCell>
                <TableCell>{feedbackTypes.find((type) => type.value === feedback.type)?.label}</TableCell>
                <TableCell>{feedback.content}</TableCell>
                <TableCell>{feedback.createdAt}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

