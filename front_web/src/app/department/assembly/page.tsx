"use client"

import { useState } from "react"
import Header from "@/components/Header"
import AssemblyDepartmentChart from "@/components/AssemblyDepartmentChart"
import WordCloud from "@/components/WordCloud"
import BudgetChart from "@/components/BudgetChart"
import DepartmentFeeds from "@/components/DepartmentFeeds"
import Footer from "@/components/Footer"
import type { FeedItem } from "@/types/feed" // type 키워드 추가

const mockAssemblyFeeds: FeedItem[] = [
  {
    article_id: 1,
    title: "국회, 새로운 법안 통과",
    summation: "오늘 국회에서는 중요한 법안이 통과되었습니다. 이 법안은 많은 국민들의 관심사였던...",
    category_id: 1,
    category_name: "분류 1",
    published_at: "2024.03.15",
  },
  {
    article_id: 2,
    title: "국회의원 윤리강령 개정안 발의",
    summation: "국회의원들의 윤리 기준을 강화하는 새로운 개정안이 발의되었습니다. 이 개정안은...",
    category_id: 1,
    category_name: "분류 2",
    published_at: "2024.03.14",
  },
  {
    article_id: 3,
    title: "국회 예산안 심사 시작",
    summation: "내년도 예산안에 대한 국회 심사가 오늘부터 시작되었습니다. 주요 쟁점은...",
    category_id: 1,
    category_name: "분류 3",
    published_at: "2024.03.13",
  },
  {
    article_id: 4,
    title: "국회 대정부질문 진행",
    summation: "이번 주 국회에서는 대정부질문이 진행됩니다. 주요 안건으로는...",
    category_id: 1,
    category_name: "분류 4",
    published_at: "2024.03.12",
  },
  {
    article_id: 5,
    title: "국회 특별위원회 구성",
    summation: "최근 이슈가 된 사안에 대해 국회 특별위원회가 구성되었습니다. 위원회는...",
    category_id: 1,
    category_name: "분류 5",
    published_at: "2024.03.11",
  },
  {
    article_id: 6,
    title: "국회의장, 주요 정당 대표 회동",
    summation: "국회의장이 여야 주요 정당 대표들과 회동을 가졌습니다. 주요 논의 사항은...",
    category_id: 1,
    category_name: "분류 1",
    published_at: "2024.03.10",
  },
  {
    article_id: 7,
    title: "국회 공청회 개최",
    summation: "주요 법안에 대한 국회 공청회가 개최되었습니다. 전문가들의 의견은...",
    category_id: 1,
    category_name: "분류 2",
    published_at: "2024.03.09",
  },
  {
    article_id: 8,
    title: "국회 인사��문회 ���시",
    summation: "새로 지명된 장관 후보자에 대한 인사청문회가 국회에서 실시되었습니다. 주요 쟁점은...",
    category_id: 1,
    category_name: "분류 3",
    published_at: "2024.03.08",
  },
  {
    article_id: 9,
    title: "국회 본회의 개최",
    summation: "이번 주 국회 본회의가 개최됩니다. 주요 안건으로는...",
    category_id: 1,
    category_name: "분류 4",
    published_at: "2024.03.07",
  },
  {
    article_id: 10,
    title: "국회 국정감사 일정 발표",
    summation: "올해 국회 국정감사 일정이 발표되었습니다. 주요 감사 대상과 일정은...",
    category_id: 1,
    category_name: "분류 5",
    published_at: "2024.03.06",
  },
]

export default function AssemblyDepartmentPage() {
  const [assemblyFeeds] = useState<FeedItem[]>(mockAssemblyFeeds)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const handleCategorySelect = (category: string) => {
    if (selectedCategory === category) {
      setSelectedCategory(null)
    } else {
      setSelectedCategory(category)
    }
  }

  const filteredFeeds = selectedCategory
    ? assemblyFeeds.filter((feed) => feed.category_name === selectedCategory)
    : assemblyFeeds

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header color="teal-600" />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <AssemblyDepartmentChart onCategorySelect={handleCategorySelect} selectedCategory={selectedCategory} />
          <WordCloud department="assembly" color="#1a7f7f" />
          <BudgetChart department="assembly" color="#1a7f7f" />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DepartmentFeeds feeds={filteredFeeds} variant="assembly" showCategoryName={true} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

