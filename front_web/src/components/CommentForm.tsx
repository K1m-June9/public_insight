"use client"

import { useState } from "react"
import { useAuth } from "../contexts/AuthContext"

interface CommentFormProps {
  onSubmit: (content: string) => void
}

export default function CommentForm({ onSubmit }: CommentFormProps) {
  const [content, setContent] = useState("")
  const { isLoggedIn } = useAuth()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (content.trim()) {
      if (isLoggedIn) {
        onSubmit(content)
        setContent("")
      } else {
        alert("댓글을 작성하려면 로그인이 필요합니다.")
      }
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-6">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        className="w-full p-2 border border-gray-300 rounded"
        placeholder="댓글을 입력하세요..."
        rows={3}
      />
      <button type="submit" className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
        댓글 작성
      </button>
    </form>
  )
}

