import { NextResponse } from "next/server"
import type { FeedItem } from "@/types/feed"

// This is a mock database. In a real application, you would fetch this data from your actual database.
const mockDatabase: FeedItem[] = [
  {
    article_id: 1,
    title: "신규 일자리 창출 정책 발표",
    summation: "정부가 청년 실업률 감소를 위한 새로운 일자리 창출 정책을 발표했습니다.",
    category_id: 4,
    published_at: "2024.03.15",
  },
  {
    article_id: 2,
    title: "교육부, 새 학기 교육 정책 발표",
    summation: "교육부가 새 학기를 맞아 새로운 교육 정책을 발표했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.14",
  },
  {
    article_id: 3,
    title: "여성가족부, 성평등 정책 추진 계획 발표",
    summation: "여성가족부가 올해의 성평등 정책 추진 계획을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.13",
  },
  // Add more mock data as needed
]

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get("q")

  if (!query) {
    return NextResponse.json({ error: "Query parameter is required" }, { status: 400 })
  }

  // Perform a case-insensitive search on title and summation
  const results = mockDatabase.filter(
    (item) =>
      item.title.toLowerCase().includes(query.toLowerCase()) ||
      item.summation.toLowerCase().includes(query.toLowerCase()),
  )

  return NextResponse.json(results)
}

