"use client"

import { ArrowLeft, ThumbsUp, ThumbsDown, Bookmark } from "lucide-react"
import { useRouter } from "next/navigation"
import Header from "./Header"
import Footer from "./Footer"
import { useState } from "react"
import { getCategoryName } from "../types/feed"
import Comment from "./Comment"
import CommentForm from "./CommentForm"
import { useAuth } from "../contexts/AuthContext"

// 댓글 응답 타입 정의
interface CommentReply {
  id: number
  author: string
  content: string
  likes: number
  dislikes: number
  replies: CommentReply[]
  isDeleted: boolean
  createdAt?: string // 이 속성도 추가
}

interface FeedDetailProps {
  article_id: number
  title: string
  content: string
  author_id?: string
  category_id: number
  published_at: string
  Link_to_original_material: string
  view_count: number
  organization_subcategory: string
  likes: number
  dislikes: number
  comments?: {
    id: number
    author: string
    content: string
    likes: number
    dislikes: number
    replies: CommentReply[]
    isDeleted: boolean
    createdAt?: string
  }[]
  showComments?: boolean
}

export default function FeedDetail({
  title,
  content,
  author_id,
  category_id,
  published_at,
  Link_to_original_material,
  view_count,
  organization_subcategory,
  likes: initialLikes,
  dislikes: initialDislikes,
  comments: initialComments = [],
  showComments = true,
}: FeedDetailProps) {
  const router = useRouter()
  const [liked, setLiked] = useState(false)
  const [disliked, setDisliked] = useState(false)
  const [bookmarked, setBookmarked] = useState(false)
  const [likes, setLikes] = useState(initialLikes)
  const [dislikes, setDislikes] = useState(initialDislikes)
  const [comments, setComments] = useState(initialComments || [])
  const { isLoggedIn, user } = useAuth()

  if (!comments || comments.length === 0) {
    const exampleComments = [
      {
        id: 1,
        author: "시민A",
        content: "이 정책에 대해 더 자세히 알고 싶습니다.",
        likes: 5,
        dislikes: 1,
        replies: [
          {
            id: 2,
            author: "전문가B",
            content: "이 정책의 주요 목표는 경제 활성화와 일자리 창출입니다.",
            likes: 3,
            dislikes: 0,
            replies: [],
            isDeleted: false,
          },
        ],
        isDeleted: false,
      },
      {
        id: 3,
        author: "시민C",
        content: "이 정책이 실제로 효과가 있을지 의문입니다.",
        likes: 2,
        dislikes: 2,
        replies: [],
        isDeleted: false,
      },
    ]
    setComments(exampleComments)
  }

  const handleLike = () => {
    if (isLoggedIn) {
      if (liked) {
        setLikes((prev) => prev - 1)
        setLiked(false)
      } else {
        if (disliked) {
          setDislikes((prev) => prev - 1)
          setDisliked(false)
        }
        setLikes((prev) => prev + 1)
        setLiked(true)
      }
    } else {
      alert("좋아요를 누르려면 로그인이 필요합니다.")
    }
  }

  const handleDislike = () => {
    if (isLoggedIn) {
      if (disliked) {
        setDislikes((prev) => prev - 1)
        setDisliked(false)
      } else {
        if (liked) {
          setLikes((prev) => prev - 1)
          setLiked(false)
        }
        setDislikes((prev) => prev + 1)
        setDisliked(true)
      }
    } else {
      alert("싫어요를 누르려면 로그인이 필요합니다.")
    }
  }

  const handleBookmark = () => {
    if (isLoggedIn) {
      setBookmarked(!bookmarked)
    } else {
      alert("북마크하려면 로그인이 필요합니다.")
    }
  }

  // 댓글 생성 부분에서 isDeleted 속성 추가 확인
  const handleCommentSubmit = (content: string) => {
    if (!isLoggedIn || !user) return

    const newComment = {
      id: comments.length + 1,
      author: user.nickname,
      content,
      likes: 0,
      dislikes: 0,
      replies: [],
      isDeleted: false,
      createdAt: new Date().toISOString().split("T")[0],
    }
    setComments([...comments, newComment])
  }

  // handleReply 함수에서도 isDeleted 속성 추가 확인
  const handleReply = (parentId: number, content: string) => {
    const newComments = comments.map((comment) => {
      if (comment.id === parentId) {
        return {
          ...comment,
          replies: [
            ...(comment.replies ?? []),
            {
              id: Date.now(),
              author: user?.nickname ?? "Anonymous",
              content,
              likes: 0,
              dislikes: 0,
              replies: [],
              isDeleted: false,
              createdAt: new Date().toISOString().split("T")[0],
            },
          ],
        }
      }
      return comment
    })
    setComments(newComments)
  }

  const handleLikeComment = (id: number) => {
    const newComments = comments.map((comment) =>
      comment.id === id ? { ...comment, likes: comment.likes + 1 } : comment,
    )
    setComments(newComments)
  }

  const handleDislikeComment = (id: number) => {
    const newComments = comments.map((comment) =>
      comment.id === id ? { ...comment, dislikes: comment.dislikes + 1 } : comment,
    )
    setComments(newComments)
  }

  const handleDeleteComment = (id: number) => {
    const deleteComment = (comments: CommentReply[]): CommentReply[] => {
      return comments.map((comment) => {
        if (comment.id === id) {
          return { ...comment, content: "[삭제된 댓글입니다.]", isDeleted: true }
        }
        if (comment.replies) {
          comment.replies = deleteComment(comment.replies)
        }
        return comment
      })
    }

    setComments(deleteComment(comments))
  }

  const renderComments = () => {
    if (!showComments) return null

    return (
      <>
        <h2 className="text-2xl font-bold mb-4 mt-8"></h2>
        <CommentForm onSubmit={handleCommentSubmit} />
        {comments.map((comment) => (
          <Comment
            key={comment.id}
            {...comment}
            onReply={handleReply}
            onLike={handleLikeComment}
            onDislike={handleDislikeComment}
            onDelete={handleDeleteComment}
            isAdmin={user?.isAdmin || false}
            createdAt={comment.createdAt || "2024.03.15"}
          />
        ))}
      </>
    )
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-1 bg-gray-100">
        <div className="max-w-6xl mx-auto">
          <div className="bg-white shadow-md my-6 rounded-lg">
            <div className="px-8 py-6">
              <button
                onClick={() => router.back()}
                className="flex items-center text-blue-600 hover:text-blue-700 mb-6"
              >
                <ArrowLeft className="mr-2" size={20} />
                Back
              </button>
              <h1 className="text-3xl font-bold mb-4">{title}</h1>
              <div className="flex items-center text-sm text-gray-500 mb-8">
                <span className="mr-4">{getCategoryName(category_id)}</span>
                <span className="mr-4">{organization_subcategory}</span>
                <span className="mr-4">{view_count} views</span>
                <span className="mr-4">{published_at}</span>
                {author_id && <span>Author ID: {author_id}</span>}
              </div>
              <div className="prose max-w-none mb-6">{content}</div>
              <a
                href={Link_to_original_material}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-700 block mb-8"
              >
                원문 링크
              </a>
              <div className="flex items-center justify-between py-4 border-t">
                <div className="flex items-center space-x-6">
                  <button
                    onClick={handleLike}
                    className={`flex items-center space-x-2 ${
                      liked ? "text-blue-600" : "text-gray-600 hover:text-blue-600"
                    } transition-colors`}
                  >
                    <ThumbsUp className={`w-5 h-5 ${liked ? "fill-current" : ""}`} />
                    <span>{likes}</span>
                  </button>
                  <button
                    onClick={handleDislike}
                    className={`flex items-center space-x-2 ${
                      disliked ? "text-red-600" : "text-gray-600 hover:text-red-600"
                    } transition-colors`}
                  >
                    <ThumbsDown className={`w-5 h-5 ${disliked ? "fill-current" : ""}`} />
                    <span>{dislikes}</span>
                  </button>
                </div>
                <div className="flex items-center space-x-6">
                  <button
                    onClick={handleBookmark}
                    className={`text-gray-600 hover:text-gray-800 transition-colors ${
                      bookmarked ? "text-blue-600" : ""
                    }`}
                  >
                    <Bookmark className={`w-5 h-5 ${bookmarked ? "fill-current" : ""}`} />
                  </button>
                </div>
              </div>
              {renderComments()}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}

