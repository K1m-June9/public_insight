"use client"

import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import FeedDetail from "@/components/FeedDetail"
import type { FeedDetail as FeedDetailType } from "@/types/feed" // type 키워드 추가

export default function FeedPage() {
  const { id } = useParams()
  const [feedData, setFeedData] = useState<FeedDetailType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchFeedData() {
      try {
        const res = await fetch(`/api/feeds?id=${id}`)
        if (!res.ok) {
          throw new Error("Failed to fetch feed")
        }
        const data = await res.json()

        // 댓글 데이터에 isDeleted 속성 추가
        if (data.comments) {
          // 재귀적으로 모든 댓글과 대댓글에 isDeleted 속성 추가하는 함수
          const addIsDeletedProperty = (comment: any): any => {
            return {
              ...comment,
              isDeleted: false, // 명시적으로 false로 설정
              createdAt: comment.createdAt || "2024.03.15", // createdAt 속성 추가
              replies: Array.isArray(comment.replies) 
                ? comment.replies.map(addIsDeletedProperty) 
                : []
            };
          };
          
          data.comments = data.comments.map(addIsDeletedProperty);
        }

        setFeedData(data)
      } catch (err) {
        console.error("Failed to load feed:", err)
        setError("Failed to load feed. Please try again later.")
      } finally {
        setIsLoading(false)
      }
    }

    if (id) {
      fetchFeedData()
    }
  }, [id])

  if (isLoading) {
    return <div className="text-center text-gray-500 text-xl mt-8">Loading...</div>
  }

  if (error) {
    return <div className="text-center text-red-500 text-xl mt-8">Error: {error}</div>
  }

  if (!feedData) {
    return <div className="text-center text-gray-500 text-xl mt-8">Feed not found</div>
  }

  return <FeedDetail {...feedData} comments={feedData.comments || []} />
}

