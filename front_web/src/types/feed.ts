// 댓글 응답 타입 정의
export interface CommentReply {
  id: number
  author: string
  content: string
  likes: number
  dislikes: number
  replies: CommentReply[]
  isDeleted: boolean
  createdAt?: string // 날짜 정보 추가
}

export interface FeedItem {
  article_id: number
  title: string
  summation: string
  category_id: number
  category_name?: string
  published_at: string
  likes?: number
  dislikes?: number
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
}

export interface FeedDetail extends FeedItem {
  content: string
  author_id?: string
  Link_to_original_material: string
  view_count: number
  organization_subcategory: string
  likes: number
  dislikes: number
}

export const getCategoryName = (category_id: number): string => {
  const categories: { [key: number]: string } = {
    1: "국회",
    2: "교육부",
    3: "여성가족부",
    4: "고용노동부",
    5: "문화체육관광부",
    // 필요에 따라 더 많은 카테고리를 추가할 수 있습니다.
  }
  return categories[category_id] || "기타"
}

