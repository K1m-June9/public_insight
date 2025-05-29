"use client"

import { useState } from "react"
import Header from "@/components/Header"
import EducationDepartmentChart from "@/components/EducationDepartmentChart"
import WordCloud from "@/components/WordCloud"
import BudgetChart from "@/components/BudgetChart"
import DepartmentFeeds from "@/components/DepartmentFeeds"
import Footer from "@/components/Footer"
import type { FeedItem } from "@/types/feed" // type 키워드 추가

const mockEducationFeeds: FeedItem[] = [
  {
    article_id: 11,
    title: "교육부, 새 학기 교육 정책 발표",
    summation: "교육부가 새 학기를 맞아 새로운 교육 정책을 발표했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.15",
    category_name: "분류 1",
  },
  {
    article_id: 12,
    title: "초등학교 교과서 개정안 확정",
    summation: "교육부가 초등학교 교과서 개정안을 최종 확정했습니다. 주요 변경 사항은...",
    category_id: 2,
    published_at: "2024.03.14",
    category_name: "분류 2",
  },
  {
    article_id: 13,
    title: "대학입시 제도 개선 방안 논의",
    summation: "교육부가 대학입시 제도 개선을 위한 공청회를 개최했습니다. 주요 논의 사항은...",
    category_id: 2,
    published_at: "2024.03.13",
    category_name: "분류 3",
  },
  {
    article_id: 14,
    title: "교원 평가 시스템 개편 추진",
    summation: "교육부가 교원 평가 시스템 개편을 추진한다고 밝혔습니다. 주요 내용은...",
    category_id: 2,
    published_at: "2024.03.12",
    category_name: "분류 4",
  },
  {
    article_id: 15,
    title: "학교 폭력 예방 대책 강화",
    summation: "교육부가 학교 폭력 예방을 위한 새로운 대책을 발표했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.11",
    category_name: "분류 5",
  },
  {
    article_id: 16,
    title: "디지털 교육 인프라 확충 계획 발표",
    summation: "교육부가 디지털 교육 인프라 확충을 위한 중장기 계획을 발표했습니다. 주요 내용은...",
    category_id: 2,
    published_at: "2024.03.10",
    category_name: "분류 1",
  },
  {
    article_id: 17,
    title: "특수교육 지원 확대 방안 마련",
    summation: "교육부가 특수교육 대상 학생들을 위한 지원 확대 방안을 마련했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.09",
    category_name: "분류 2",
  },
  {
    article_id: 18,
    title: "교육 격차 해소를 위한 정책 발표",
    summation: "교육부가 지역 간, 계층 간 교육 격차 해소를 위한 새로운 정책을 발표했습니다. 주요 내용은...",
    category_id: 2,
    published_at: "2024.03.08",
    category_name: "분류 3",
  },
  {
    article_id: 19,
    title: "학생 정신 건강 지원 강화 방안",
    summation: "교육부가 학생들의 정신 건강 지원을 강화하기 위한 새로운 방안을 발표했습니다. 주요 내용으로는...",
    category_id: 2,
    published_at: "2024.03.07",
    category_name: "분류 4",
  },
  {
    article_id: 20,
    title: "미래 교육 혁신 로드맵 발표",
    summation: "교육부가 미래 교육 혁신을 위한 중장기 로드맵을 발표했습니다. 주요 내용은...",
    category_id: 2,
    published_at: "2024.03.06",
    category_name: "분류 5",
  },
]

export default function EducationDepartmentPage() {
  const [educationFeeds] = useState<FeedItem[]>(mockEducationFeeds)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const handleCategorySelect = (category: string) => {
    if (selectedCategory === category) {
      setSelectedCategory(null)
    } else {
      setSelectedCategory(category)
    }
  }

  const filteredFeeds = selectedCategory
    ? educationFeeds.filter((feed) => feed.category_name === selectedCategory)
    : educationFeeds

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header color="green-600" />
      <main className="flex-1 flex overflow-hidden">
        <div className="w-[45%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <EducationDepartmentChart onCategorySelect={handleCategorySelect} selectedCategory={selectedCategory} />
          <WordCloud department="education" color="#1a4d1a" />
          <BudgetChart department="education" color="#1a4d1a" />
        </div>
        <div className="w-[55%] overflow-y-auto h-[calc(100vh-64px)] custom-scrollbar">
          <DepartmentFeeds feeds={filteredFeeds} variant="education" showCategoryName={true} />
        </div>
      </main>
      <Footer />
    </div>
  )
}

