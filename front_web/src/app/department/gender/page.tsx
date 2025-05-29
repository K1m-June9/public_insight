"use client"

import { useState } from "react"
import Header from "@/components/Header"
import GenderDepartmentChart from "@/components/GenderDepartmentChart"
import WordCloud from "@/components/WordCloud"
import BudgetChart from "@/components/BudgetChart"
import DepartmentFeeds from "@/components/DepartmentFeeds"
import Footer from "@/components/Footer"
import type { FeedItem } from "@/types/feed" // type 키워드 추가

const mockGenderFeeds: FeedItem[] = [
  {
    article_id: 21,
    title: "여성가족부, 성평등 정책 추진 계획 발표",
    summation: "여성가족부가 올해의 성평등 정책 추진 계획을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.15",
    category_name: "분류 1",
  },
  {
    article_id: 22,
    title: "가정폭력 피해자 지원 강화 방안 마련",
    summation: "여성가족부가 가정폭력 피해자 지원을 강화하기 위한 새로운 방안을 마련했습니다. 주요 내용으로는...",
    category_id: 3,
    published_at: "2024.03.14",
    category_name: "분류 2",
  },
  {
    article_id: 23,
    title: "청소년 정책 종합계획 발표",
    summation: "여성가족부가 청소년 정책 종합계획을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.13",
    category_name: "분류 3",
  },
  {
    article_id: 24,
    title: "일·가정 양립 지원 정책 확대",
    summation: "여성가족부가 일·가정 양립 지원을 위한 새로운 정책을 발표했습니다. 주요 내용으로는...",
    category_id: 3,
    published_at: "2024.03.12",
    category_name: "분류 4",
  },
  {
    article_id: 25,
    title: "성폭력 예방 교육 강화 방안",
    summation: "여성가족부가 성폭력 예방 교육을 강화하기 위한 새로운 방안을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.11",
    category_name: "분류 5",
  },
  {
    article_id: 26,
    title: "한부모 가족 지원 확대 계획",
    summation: "여성가족부가 한부모 가족 지원을 확대하기 위한 새로운 계획을 발표했습니다. 주요 내용으로는...",
    category_id: 3,
    published_at: "2024.03.10",
    category_name: "분류 1",
  },
  {
    article_id: 27,
    title: "여성 경제활동 지원 정책 발표",
    summation: "여성가족부가 여성의 경제활동을 지원하기 위한 새로운 정책을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.09",
    category_name: "분류 2",
  },
  {
    article_id: 28,
    title: "다문화 가족 지원 강화 방안",
    summation: "여성가족부가 다문화 가족 지원을 강화하기 위한 새로운 방안을 발표했습니다. 주요 내용으로는...",
    category_id: 3,
    published_at: "2024.03.08",
    category_name: "분류 3",
  },
  {
    article_id: 29,
    title: "아동 권리 보호 정책 발표",
    summation: "여성가족부가 아동 권리 보호를 위한 새로운 정책을 발표했습니다. 주요 내용은...",
    category_id: 3,
    published_at: "2024.03.07",
    category_name: "분류 4",
  },
  {
    article_id: 30,
    title: "성평등 문화 확산을 위한 캠페인 시작",
    summation: "여성가족부가 성평등 문화 확산을 위한 새로운 캠페인을 시작했습니다. 주요 내용으로는...",
    category_id: 3,
    published_at: "2024.03.06",
    category_name: "분류 5",
  },
]

export default function GenderDepartmentPage() {
  const [genderFeeds] = useState<FeedItem[]>(mockGenderFeeds)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const handleCategorySelect = (category: string) => {
    if (selectedCategory === category) {
      setSelectedCategory(null)
    } else {
      setSelectedCategory(category)
    }
  }

  const filteredFeeds = selectedCategory
    ? genderFeeds.filter((feed) => feed.category_name === selectedCategory)
    : genderFeeds

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header color="purple-600" />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] bg-white border-r overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <GenderDepartmentChart onCategorySelect={handleCategorySelect} selectedCategory={selectedCategory} />
          <WordCloud department="gender" color="#8A2BE2" />
          <BudgetChart department="gender" />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DepartmentFeeds feeds={filteredFeeds} variant="gender" showCategoryName={true} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

