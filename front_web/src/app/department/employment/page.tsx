"use client"

import { useState } from "react"
import Header from "@/components/Header"
import EmploymentDepartmentChart from "@/components/EmploymentDepartmentChart"
import WordCloud from "@/components/WordCloud"
import BudgetChart from "@/components/BudgetChart"
import DepartmentFeeds from "@/components/DepartmentFeeds"
import Footer from "@/components/Footer"
import type { FeedItem } from "@/types/feed" // type 키워드 추가

const mockEmploymentFeeds: FeedItem[] = [
  {
    article_id: 31,
    title: "고용노동부, 일자리 창출 방안 발표",
    summation: "고용노동부가 새로운 일자리 창출 방안을 발표했습니다. 주요 정책으로는...",
    category_id: 4,
    published_at: "2024.03.15",
    category_name: "정책 발표",
  },
  {
    article_id: 32,
    title: "최저임금 인상안 확정",
    summation: "고용노동부가 내년도 최저임금 인상안을 확정 발표했습니다. 주요 내용은...",
    category_id: 4,
    published_at: "2024.03.14",
    category_name: "정책 발표",
  },
  {
    article_id: 33,
    title: "근로시간 단축 정책 추진",
    summation: "고용노동부가 근로시간 단축을 위한 새로운 정책을 추진한다고 밝혔습니다. 주요 내용으로는...",
    category_id: 4,
    published_at: "2024.03.13",
    category_name: "정책 발표",
  },
  {
    article_id: 34,
    title: "청년 취업 지원 프로그램 확대",
    summation: "고용노동부가 청년 취업 지원 프로그램을 확대한다고 발표했습니다. 주요 내용은...",
    category_id: 4,
    published_at: "2024.03.12",
    category_name: "정책 발표",
  },
  {
    article_id: 35,
    title: "산업안전보건법 개정안 발표",
    summation: "고용노동부가 산업안전보건법 개정안을 발표했습니다. 주요 변경 사항은...",
    category_id: 4,
    published_at: "2024.03.11",
    category_name: "법률 개정",
  },
  {
    article_id: 36,
    title: "비정규직 처우 개선 대책 마련",
    summation: "고용노동부가 비정규직 근로자의 처우 개선을 위한 새로운 대책을 마련했습니다. 주요 내용으로는...",
    category_id: 4,
    published_at: "2024.03.10",
    category_name: "정책 발표",
  },
  {
    article_id: 37,
    title: "직업훈련 지원 확대 계획 발표",
    summation: "고용노동부가 직업훈련 지원을 확대하기 위한 새로운 계획을 발표했습니다. 주요 내용은...",
    category_id: 4,
    published_at: "2024.03.09",
    category_name: "정책 발표",
  },
  {
    article_id: 38,
    title: "노사관계 개선을 위한 정책 추진",
    summation: "고용노동부가 노사관계 개선을 위한 새로운 정책을 추진한다고 밝혔습니다. 주요 내용으로는...",
    category_id: 4,
    published_at: "2024.03.08",
    category_name: "정책 발표",
  },
  {
    article_id: 39,
    title: "외국인 근로자 고용 제도 개선",
    summation: "고용노동부가 외국인 근로자 고용 제도 개선 방안을 발표했습니다. 주요 내용은...",
    category_id: 4,
    published_at: "2024.03.07",
    category_name: "제도 개선",
  },
  {
    article_id: 40,
    title: "일자리 안정자금 지원 확대",
    summation: "고용노동부가 일자리 안정자금 지원을 확대한다고 발표했습니다. 주요 내용으로는...",
    category_id: 4,
    published_at: "2024.03.06",
    category_name: "정책 발표",
  },
]

export default function EmploymentDepartmentPage() {
  const [employmentFeeds] = useState<FeedItem[]>(mockEmploymentFeeds)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const handleCategorySelect = (category: string) => {
    if (selectedCategory === category) {
      setSelectedCategory(null)
    } else {
      setSelectedCategory(category)
    }
  }

  const filteredFeeds = selectedCategory
    ? employmentFeeds.filter((feed) => feed.category_name === selectedCategory)
    : employmentFeeds

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header color="amber-600" />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <EmploymentDepartmentChart onCategorySelect={handleCategorySelect} selectedCategory={selectedCategory} />
          <WordCloud department="employment" color="#8B4513" />
          <BudgetChart department="employment" />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DepartmentFeeds feeds={filteredFeeds} variant="employment" showCategoryName={true} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

