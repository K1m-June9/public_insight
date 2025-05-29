"use client"

import { useState } from "react"
import { ThumbsUp, ThumbsDown, MessageSquare, Trash2, Flag } from 'lucide-react'
import { useAuth } from "../contexts/AuthContext"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import type { CommentReply } from "@/types/feed" // type 키워드 추가

interface CommentProps {
  id: number
  author: string
  content: string
  likes: number
  dislikes: number
  replies: CommentReply[]
  onReply: (parentId: number, content: string) => void
  onLike: (id: number) => void
  onDislike: (id: number) => void
  onDelete: (id: number) => void
  isReply?: boolean
  isAdmin: boolean
  createdAt: string
  isDeleted: boolean
}

export default function Comment({
  id,
  author,
  content,
  likes,
  dislikes,
  replies,
  onReply,
  onLike,
  onDislike,
  onDelete,
  isReply = false,
  isAdmin,
  createdAt,
  isDeleted,
}: CommentProps) {
  const [isReplying, setIsReplying] = useState(false)
  const [replyContent, setReplyContent] = useState("")
  const { isLoggedIn } = useAuth()
  const [isReportOpen, setIsReportOpen] = useState(false)
  const [reportReason, setReportReason] = useState("")

  const handleReply = () => {
    if (isLoggedIn) {
      setIsReplying(!isReplying)
    } else {
      alert("댓글을 작성하려면 로그인이 필요합니다.")
    }
  }

  const submitReply = () => {
    if (replyContent.trim()) {
      onReply(id, replyContent)
      setReplyContent("")
      setIsReplying(false)
    }
  }

  const handleLike = () => {
    if (isLoggedIn) {
      onLike(id)
    } else {
      alert("좋아요를 누르려면 로그인이 필요합니다.")
    }
  }

  const handleDislike = () => {
    if (isLoggedIn) {
      onDislike(id)
    } else {
      alert("싫어요를 누르려면 로그인이 필요합니다.")
    }
  }

  const handleDelete = () => {
    if (isAdmin) {
      onDelete(id)
    }
  }

  const handleReport = () => {
    if (isLoggedIn) {
      if (reportReason) {
        alert(`댓글이 '${reportReason}'의 사유로 신고되었습니다.`)
        setIsReportOpen(false)
        setReportReason("")
      } else {
        alert("신고 사유를 선택해주세요.")
      }
    } else {
      alert("댓글을 신고하려면 로그인이 필요합니다.")
    }
  }

  return (
    <div className={`border-b border-gray-200 py-4 ${isReply ? "ml-8" : ""}`}>
      <div className="flex items-start justify-between">
        <div className="flex-grow">
          <div className="flex items-center">
            <p className="font-semibold">{author}</p>
            <span className="text-sm text-gray-500 ml-2">• {createdAt}</span>
          </div>
          {isDeleted ? (
            <p className="mt-1 text-gray-400 italic">[삭제된 댓글입니다.]</p>
          ) : (
            <p className="mt-1 text-gray-600">{content}</p>
          )}
          {!isDeleted && (
            <div className="mt-2 flex items-center space-x-4">
              <button onClick={handleLike} className="flex items-center text-gray-500 hover:text-blue-500">
                <ThumbsUp size={16} className="mr-1" />
                <span>{likes}</span>
              </button>
              <button onClick={handleDislike} className="flex items-center text-gray-500 hover:text-red-500">
                <ThumbsDown size={16} className="mr-1" />
                <span>{dislikes}</span>
              </button>
              {!isReply && (
                <button onClick={handleReply} className="flex items-center text-gray-500 hover:text-gray-700">
                  <MessageSquare size={16} className="mr-1" />
                  
                </button>
              )}
              {isAdmin && (
                <Button variant="destructive" size="sm" onClick={handleDelete}>
                  <Trash2 size={16} className="mr-1" />
                  삭제
                </Button>
              )}
            </div>
          )}
        </div>
        {!isDeleted && (
          <Popover open={isReportOpen} onOpenChange={setIsReportOpen}>
            <PopoverTrigger asChild>
              <Button variant="outline" size="sm">
                <Flag size={16} className="mr-1" />
                신고
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">신고</h4>
                  <p className="text-sm text-muted-foreground">이 댓글을 신고하는 사유를 선택해주세요.</p>
                </div>
                <div className="grid gap-2">
                  <Select onValueChange={setReportReason}>
                    <SelectTrigger>
                      <SelectValue placeholder="신고 사유 선택" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="사유1">사유1</SelectItem>
                      <SelectItem value="사유2">사유2</SelectItem>
                      <SelectItem value="사유3">사유3</SelectItem>
                      <SelectItem value="사유4">사유4</SelectItem>
                      <SelectItem value="사유5">사유5</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button onClick={handleReport}>신고하기</Button>
                </div>
              </div>
            </PopoverContent>
          </Popover>
        )}
      </div>
      {isReplying && (
        <div className="mt-3">
          <textarea
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            className="w-full p-2 border border-gray-300 rounded"
            placeholder="답글을 입력하세요..."
          />
          <button onClick={submitReply} className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
            작성
          </button>
        </div>
      )}
      {replies.length > 0 && (
        <div className="mt-4">
          {replies.map((reply) => (
            <Comment
              key={reply.id}
              {...reply}
              onReply={onReply}
              onLike={onLike}
              onDislike={onDislike}
              onDelete={onDelete}
              isReply={true}
              isAdmin={isAdmin}
              createdAt={reply.createdAt || "2024.03.15"}
            />
          ))}
        </div>
      )}
    </div>
  )
}

