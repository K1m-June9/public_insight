"use client"

import type React from "react"

import { useState } from "react"
import { Bookmark } from "lucide-react"
import Link from "next/link"
import { type FeedItem as FeedItemType, getCategoryName } from "../types/feed"
import { useAuth } from "../contexts/AuthContext"

interface FeedItemProps extends FeedItemType {
  variant?: "default" | "assembly" | "education" | "gender" | "employment" | "culture"
  showCategoryName?: boolean
}

const variantColors = {
  default: "bg-blue-100 text-blue-600",
  assembly: "bg-[#E0FFFF] text-[#20B2AA]",
  education: "bg-[#E8F5E9] text-[#1a4d1a]",
  gender: "bg-[#E6E6FA] text-[#8A2BE2]",
  employment: "bg-[#FFF5E6] text-[#8B4513]",
  culture: "bg-[#FFF5E6] text-[#FFA500]",
}

const bookmarkColors = {
  default: "text-blue-600",
  assembly: "text-[#20B2AA]",
  education: "text-[#1a4d1a]",
  gender: "text-[#8A2BE2]",
  employment: "text-[#8B4513]",
  culture: "text-[#FFA500]",
}

export default function FeedItem({
  article_id,
  title,
  summation,
  category_id,
  category_name,
  published_at,
  variant = "default",
  showCategoryName = false,
}: FeedItemProps) {
  const [isBookmarked, setIsBookmarked] = useState(false)
  const { isLoggedIn } = useAuth()

  const toggleBookmark = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    if (isLoggedIn) {
      setIsBookmarked(!isBookmarked)
    } else {
      alert("북마크하려면 로그인이 필요합니다.")
    }
  }

  const tagColorClass = variantColors[variant]
  const bookmarkColorClass = bookmarkColors[variant]

  const categoryDisplayName = showCategoryName && category_name ? category_name : getCategoryName(category_id)

  return (
    <div className="bg-white rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow block mb-2">
      <Link href={`/feed/${article_id}`} className="block">
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-lg font-medium mb-2">{title}</h3>
            <p className="text-gray-600 text-sm mb-2 line-clamp-2">{summation}</p>
            <div className="mt-2 flex gap-2">
              <span className={`text-xs px-2 py-1 rounded-full ${tagColorClass}`}>{categoryDisplayName}</span>
              <span className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">{published_at}</span>
            </div>
          </div>
          <button
            onClick={toggleBookmark}
            className={`${bookmarkColorClass} hover:opacity-80 transition-opacity ${isBookmarked ? "opacity-100" : "opacity-50"}`}
          >
            <Bookmark size={20} className={isBookmarked ? "fill-current" : ""} />
          </button>
        </div>
      </Link>
    </div>
  )
}

