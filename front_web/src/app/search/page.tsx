"use client"

import { useState, useEffect } from "react"
import { useSearchParams } from "next/navigation"
import Header from "@/components/Header"
import Footer from "@/components/Footer"
import FeedItem from "@/components/FeedItem"
import type { FeedItem as FeedItemType } from "@/types/feed"

export default function SearchPage() {
  const searchParams = useSearchParams()
  const query = searchParams.get("q")
  const [searchResults, setSearchResults] = useState<FeedItemType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSearchResults = async () => {
      setIsLoading(true)
      setError(null)
      try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query || "")}`)
        if (!response.ok) {
          throw new Error("Failed to fetch search results")
        }
        const data = await response.json()
        setSearchResults(data)
      } catch (err) {
        setError("Failed to load search results. Please try again.")
        console.error("Search error:", err)
      } finally {
        setIsLoading(false)
      }
    }

    if (query) {
      fetchSearchResults()
    }
  }, [query])

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-xl font-medium text-gray-900">{`'${query}' 에 대한 검색 결과`}</h1>
        </div>
        {isLoading ? (
          <div>검색 중...</div>
        ) : error ? (
          <div className="text-red-500">{error}</div>
        ) : (
          <div className="space-y-4">
            {searchResults.map((item) => (
              <FeedItem key={item.article_id} {...item} />
            ))}
            {searchResults.length === 0 && <div>검색 결과가 없습니다.</div>}
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}

