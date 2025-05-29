"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

type Report = {
  id: string
  reporterUsername: string
  reportedUsername: string
  reportedAt: string
  commentContent: string
  reason: string
}

const mockReports: Report[] = [
  {
    id: "1",
    reporterUsername: "user1",
    reportedUsername: "user2",
    reportedAt: "2024-03-20 14:30",
    commentContent: "이 댓글은 부적절한 내용을 포함하고 있습니다.",
    reason: "부적절한 내용",
  },
  {
    id: "2",
    reporterUsername: "user3",
    reportedUsername: "user4",
    reportedAt: "2024-03-21 09:15",
    commentContent: "이 댓글은 스팸 광고입니다.",
    reason: "스팸",
  },
  {
    id: "3",
    reporterUsername: "user5",
    reportedUsername: "user6",
    reportedAt: "2024-03-22 16:45",
    commentContent: "이 댓글은 다른 사용자를 모욕하고 있습니다.",
    reason: "모욕적인 내용",
  },
]

export default function ReportManagement() {
  const [reports, setReports] = useState<Report[]>(mockReports)

  const handleDeleteReport = (id: string) => {
    setReports(reports.filter((report) => report.id !== id))
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>신고 관리</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>신고자</TableHead>
              <TableHead>신고 대상</TableHead>
              <TableHead>신고 시각</TableHead>
              <TableHead>사유</TableHead>
              <TableHead>액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {reports.map((report) => (
              <TableRow key={report.id}>
                <TableCell>{report.reporterUsername}</TableCell>
                <TableCell>{report.reportedUsername}</TableCell>
                <TableCell>{report.reportedAt}</TableCell>
                <TableCell>{report.reason}</TableCell>
                <TableCell>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline">상세 보기</Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>신고 상세 정보</DialogTitle>
                        <DialogDescription>
                          <p>
                            <strong>신고자:</strong> {report.reporterUsername}
                          </p>
                          <p>
                            <strong>신고 대상:</strong> {report.reportedUsername}
                          </p>
                          <p>
                            <strong>신고 시각:</strong> {report.reportedAt}
                          </p>
                          <p>
                            <strong>사유:</strong> {report.reason}
                          </p>
                          <p>
                            <strong>댓글 내용:</strong> {report.commentContent}
                          </p>
                        </DialogDescription>
                      </DialogHeader>
                      <div className="flex justify-end space-x-2 mt-4">
                        <Button variant="destructive" onClick={() => handleDeleteReport(report.id)}>
                          삭제
                        </Button>
                        <Button variant="outline" onClick={() => handleDeleteReport(report.id)}>
                          무시
                        </Button>
                      </div>
                    </DialogContent>
                  </Dialog>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

