"use client"

import { useState } from "react"
import Header from "@/components/Header"
import CultureDepartmentChart from "@/components/CultureDepartmentChart"
import WordCloud from "@/components/WordCloud"
import BudgetChart from "@/components/BudgetChart"
import DepartmentFeeds from "@/components/DepartmentFeeds"
import Footer from "@/components/Footer"
import type { FeedItem } from "@/types/feed" // type 키워드 추가

const mockCultureFeeds: FeedItem[] = [
  {
    article_id: 41,
    title: "문화체육관광부, 관광산업 활성화 대책 발표",
    summation: "문화체육관광부가 관광산업 활성화를 위한 새로운 대책을 발표했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.15",
    category_name: "분류 1",
  },
  {
    article_id: 42,
    title: "국내 문화예술 지원 확대 계획",
    summation: "문화체육관광부가 국내 문화예술 지원을 확대하기 위한 새로운 계획을 발표했습니다. 주요 내용으로는...",
    category_id: 5,
    published_at: "2024.03.14",
    category_name: "분류 2",
  },
  {
    article_id: 43,
    title: "체육 인프라 확충 방안 마련",
    summation: "문화체육관광부가 체육 인프라 확충을 위한 새로운 방안을 마련했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.13",
    category_name: "분류 3",
  },
  {
    article_id: 44,
    title: "한류 콘텐츠 해외 진출 지원 강화",
    summation:
      "문화체육관광부가 한류 콘텐츠의 해외 진출 지원을 강화하기 위한 새로운 정책을 발표했습니다. 주요 내용으로는...",
    category_id: 5,
    published_at: "2024.03.12",
    category_name: "분류 4",
  },
  {
    article_id: 45,
    title: "문화재 보존 및 활용 종합계획 발표",
    summation: "문화체육관광부가 문화재 보존 및 활용을 위한 종합계획을 발표했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.11",
    category_name: "분류 5",
  },
  {
    article_id: 46,
    title: "국민 체육 진흥 정책 추진",
    summation: "문화체육관광부가 국민 체육 진흥을 위한 새로운 정책을 추진한다고 밝혔습니다. 주요 내용으로는...",
    category_id: 5,
    published_at: "2024.03.10",
    category_name: "분류 1",
  },
  {
    article_id: 47,
    title: "문화 다양성 증진 방안 발표",
    summation: "문화체육관광부가 문화 다양성 증진을 위한 새로운 방안을 발표했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.09",
    category_name: "분류 2",
  },
  {
    article_id: 48,
    title: "스포츠산업 육성 전략 수립",
    summation: "문화체육관광부가 스포츠산업 육성을 위한 새로운 전략을 수립했습니다. 주요 내용으로는...",
    category_id: 5,
    published_at: "2024.03.08",
    category_name: "분류 3",
  },
  {
    article_id: 49,
    title: "문화예술교육 활성화 계획 발표",
    summation: "문화체육관광부가 문화예술교육 활성화를 위한 새로운 계획을 발표했습니다. 주요 내용은...",
    category_id: 5,
    published_at: "2024.03.07",
    category_name: "분류 4",
  },
  {
    article_id: 50,
    title: "관광 벤처기업 지원 확대",
    summation: "문화체육관광부가 관광 벤처기업 지원을 확대한다고 발표했습니다. 주요 내용으로는...",
    category_id: 5,
    published_at: "2024.03.06",
    category_name: "분류 5",
  },
]

export default function CultureDepartmentPage() {
  const [cultureFeeds] = useState<FeedItem[]>(mockCultureFeeds)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const handleCategorySelect = (category: string) => {
    if (selectedCategory === category) {
      setSelectedCategory(null)
    } else {
      setSelectedCategory(category)
    }
  }

  const filteredFeeds = selectedCategory
    ? cultureFeeds.filter((feed) => feed.category_name === selectedCategory)
    : cultureFeeds

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header color="orange-600" />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <CultureDepartmentChart onCategorySelect={handleCategorySelect} selectedCategory={selectedCategory} />
          <WordCloud department="culture" color="#FFA500" />
          <BudgetChart department="culture" />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DepartmentFeeds feeds={filteredFeeds} variant="culture" showCategoryName={true} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

