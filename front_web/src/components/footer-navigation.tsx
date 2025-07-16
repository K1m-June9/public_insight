"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface FooterNavigationProps {
  currentPage: "about" | "notices" | "terms" | "privacy" | "youth-protection"
}

const pages = [
  { key: "about", title: "프로젝트 소개", path: "/about" },
  { key: "notices", title: "공지사항", path: "/notices" },
  { key: "terms", title: "이용약관", path: "/terms" },
  { key: "privacy", title: "개인정보처리방침", path: "/privacy" },
  { key: "youth-protection", title: "청소년보호정책", path: "/youth-protection" },
]

export default function FooterNavigation({ currentPage }: FooterNavigationProps) {
  return (
    <Card className="mt-12">
      <CardHeader>
        <CardTitle className="text-center">다른 페이지 보기</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {pages
            .filter((page) => page.key !== currentPage)
            .map((page) => (
              <Link key={page.key} href={page.path}>
                <Button variant="outline" className="w-full h-auto py-3 text-sm">
                  {page.title}
                </Button>
              </Link>
            ))}
        </div>
      </CardContent>
    </Card>
  )
}
