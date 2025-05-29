"use client"

import { useState } from "react"
import Header from "../components/Header"
import DataChart from "../components/DataChart"
import WeatherGrid from "../components/WeatherGrid"
import ContentCards from "../components/ContentCards"
import TopFeeds from "../components/TopFeeds"
import Footer from "../components/Footer"
import type { FeedItem } from "@/types/feed"

// Comment 타입 정의는 사용되지 않으므로 제거

const mockMainPageFeeds: FeedItem[] = [
  {
    article_id: 1,
    title: "국회, 새로운 법안 통과",
    summation: "오늘 국회에서는 중요한 법안이 통과되었습니다. 이 법안은 많은 국민들의 관심사였던...",
    category_id: 1,
    published_at: "2024.03.15",
    comments: [
      {
        id: 1,
        author: "시민1",
        content: "이 법안이 우리 사회에 어떤 영향을 미칠지 궁금합니다.",
        likes: 5,
        dislikes: 1,
        replies: [
          {
            id: 1,
            author: "전문가A",
            content: "이 법안은 주로 경제 분야에 영향을 줄 것으로 예상됩니다.",
            likes: 3,
            dislikes: 0,
            replies: [],
            isDeleted: false,
          },
        ],
        isDeleted: false,
      },
      {
        id: 2,
        author: "시민2",
        content: "법안 내용에 대해 더 자세히 알고 싶어요.",
        likes: 2,
        dislikes: 0,
        replies: [],
        isDeleted: false,
      },
    ],
  },
  {
    article_id: 11,
    title: "교육부, 새 학기 교육 정책 발표",
    summation: "교육부가 새 학기를 맞아 새로운 교육 정책을 발표했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.15",
    comments: [
      {
        id: 1,
        author: "학부모A",
        content: "새로운 정책이 학생들에게 어떤 영향을 줄까요?",
        likes: 4,
        dislikes: 1,
        replies: [],
        isDeleted: false,
      },
    ],
  },
  {
    article_id: 21,
    title: "여성가족부, 성평등 정책 추진 계획 발표",
    summation: "여성가족부가 올해의 성평등 정책 추진 계획을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.15",
    comments: [],
  },
  {
    article_id: 31,
    title: "고용노동부, 일자리 창출 방안 발표",
    summation: "고용노동부가 새로운 일자리 창출 방안을 발표했습니다. 주요 정책으로는...",
    category_id: 4,
    published_at: "2024.03.15",
    comments: [],
  },
  {
    article_id: 41,
    title: "문화체육관광부, 관광산업 활성화 대책 발표",
    summation: "문화체육관광부가 관광산업 활성화를 위한 새로운 대책을 발표했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.15",
    comments: [],
  },
]

const mockTopFeeds = [
  { id: 1, title: "국회, 새로운 법안 통과", views: 1500, likes: 230, dislikes: 20, comments: 45, department: "국회" },
  {
    id: 2,
    title: "교육부, 새 학기 교육 정책 발표",
    views: 1200,
    likes: 180,
    dislikes: 15,
    comments: 30,
    department: "교육부",
  },
  {
    id: 3,
    title: "고용노동부, 일자리 창출 방안 발표",
    views: 1000,
    likes: 150,
    dislikes: 10,
    comments: 25,
    department: "고용노동부",
  },
]

export default function Home() {
  const [feeds] = useState<FeedItem[]>(mockMainPageFeeds)
  // 로딩 상태와 에러 상태는 현재 사용되지 않으므로 제거

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] bg-white border-r overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DataChart />
          <TopFeeds feeds={mockTopFeeds} />
          <WeatherGrid />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <ContentCards feeds={feeds} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

