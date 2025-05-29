"use client"

import type React from "react"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useState } from "react"
import { Search, Bell, LogIn, UserPlus, MessageSquare } from "lucide-react"
import { useAuth } from "../contexts/AuthContext"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import FeedbackModal from "./FeedbackModal"

export default function Header({ color = "blue-800" }: { color?: string }) {
  const router = useRouter()
  // pathname은 사용되지 않으므로 제거
  const [searchQuery, setSearchQuery] = useState("")
  const { isLoggedIn, user, logout, notifications, markNotificationsAsRead } = useAuth()
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`)
    }
  }

  const getFocusRingClass = () => {
    switch (color) {
      case "teal-600":
        return "focus:ring-teal-600"
      case "green-600":
        return "focus:ring-green-600"
      case "purple-600":
        return "focus:ring-purple-600"
      case "amber-600":
        return "focus:ring-amber-600"
      case "orange-600":
        return "focus:ring-orange-600"
      default:
        return "focus:ring-blue-800"
    }
  }

  const unreadNotifications = notifications.filter((n) => !n.read)

  return (
    <header className="flex items-center justify-between px-2 py-2 border-b bg-white">
      <div className="flex items-center space-x-1">
        <Link
          href="/"
          className={`text-xl font-medium ${color === "blue-800" ? "text-blue-800" : color === "teal-600" ? "text-teal-600" : color === "green-600" ? "text-green-600" : color === "purple-600" ? "text-purple-600" : color === "amber-600" ? "text-amber-600" : color === "orange-600" ? "text-orange-600" : "text-blue-800"}`}
        >
          Public Insight
        </Link>
        {isLoggedIn ? (
          <button
            onClick={() => setIsFeedbackModalOpen(true)}
            className={`p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 ${getFocusRingClass()} relative`}
            aria-label="피드백"
          >
            <MessageSquare
              size={20}
              className={`${color === "blue-800" ? "text-blue-800" : color === "teal-600" ? "text-teal-600" : color === "green-600" ? "text-green-600" : color === "purple-600" ? "text-purple-600" : color === "amber-600" ? "text-amber-600" : color === "orange-600" ? "text-orange-600" : "text-blue-800"}`}
            />
          </button>
        ) : (
          <button
            onClick={() => alert("피드백을 남기려면 로그인이 필요합니다.")}
            className={`p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 ${getFocusRingClass()} relative`}
            aria-label="피드백"
          >
            <MessageSquare
              size={20}
              className={`${color === "blue-800" ? "text-blue-800" : color === "teal-600" ? "text-teal-600" : color === "green-600" ? "text-green-600" : color === "purple-600" ? "text-purple-600" : color === "amber-600" ? "text-amber-600" : color === "orange-600" ? "text-orange-600" : "text-blue-800"}`}
            />
          </button>
        )}
      </div>
      <div className="flex-1 max-w-xl mx-4">
        <form onSubmit={handleSearch} className="relative">
          <input
            type="text"
            placeholder="검색"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={`w-full px-4 py-2 bg-gray-100 rounded-full focus:outline-none focus:ring-2 ${getFocusRingClass()} focus:border-transparent`}
          />
          <button
            type="submit"
            className={`absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 ${
              color === "blue-800"
                ? "hover:text-blue-800"
                : color === "teal-600"
                  ? "hover:text-teal-600"
                  : color === "green-600"
                    ? "hover:text-green-600"
                    : color === "purple-600"
                      ? "hover:text-purple-600"
                      : color === "amber-600"
                        ? "hover:text-amber-600"
                        : color === "orange-600"
                          ? "hover:text-orange-600"
                          : "hover:text-blue-800"
            }`}
          >
            <Search size={20} />
          </button>
        </form>
      </div>
      <div className="flex items-center space-x-4">
        {isLoggedIn ? (
          <>
            {user?.isAdmin ? (
              <Link
                href="/admin"
                className={`text-${color} hover:underline transition-all duration-200 hover:text-opacity-70`}
              >
                AdminPage
              </Link>
            ) : (
              <>
                <Popover>
                  <PopoverTrigger asChild>
                    <button
                      className={`p-2 rounded-full hover:bg-gray-100 focus:outline-none focus:ring-2 ${getFocusRingClass()} relative`}
                      aria-label="알림"
                      onClick={markNotificationsAsRead}
                    >
                      <Bell size={20} className={`text-${color}`} />
                      {unreadNotifications.length > 0 && (
                        <span className="absolute top-0 right-0 w-2 h-2 bg-red-600 rounded-full"></span>
                      )}
                    </button>
                  </PopoverTrigger>
                  <PopoverContent className="w-80">
                    <div className="space-y-2">
                      <h3 className="font-semibold">알림</h3>
                      {notifications.length > 0 ? (
                        notifications.map((notification) => (
                          <div key={notification.id} className="text-sm">
                            {notification.content}
                          </div>
                        ))
                      ) : (
                        <div className="text-sm text-gray-500">알림이 없습니다.</div>
                      )}
                      <Link href="/mypage?tab=notifications" className="block text-sm text-blue-500 hover:underline">
                        이전 알림 보기
                      </Link>
                    </div>
                  </PopoverContent>
                </Popover>
                <Link
                  href="/mypage"
                  className={`text-${color} hover:underline transition-all duration-200 hover:text-opacity-70`}
                >
                  MyPage
                </Link>
              </>
            )}
            <button onClick={logout} className={`text-${color} hover:underline`}>
              Logout
            </button>
          </>
        ) : (
          <>
            <Link
              href="/login"
              className={`flex items-center ${color ? `text-${color}` : "text-blue-800"} hover:underline`}
            >
              <LogIn size={20} className="mr-1" />
              Log In
            </Link>
            <Link
              href="/signup"
              className={`flex items-center ${color ? `text-${color}` : "text-blue-800"} hover:underline`}
            >
              <UserPlus size={20} className="mr-1" />
              Sign Up
            </Link>
          </>
        )}
      </div>
      {isFeedbackModalOpen && (
        <FeedbackModal isOpen={isFeedbackModalOpen} onClose={() => setIsFeedbackModalOpen(false)} />
      )}
    </header>
  )
}

