import FeedItem from "./FeedItem"
import { memo } from "react"
import type { FeedItem as FeedItemType } from "../types/feed" // type 키워드 추가

interface DepartmentFeedsProps {
  feeds: FeedItemType[] // 타입으로 명시적 사용
  variant: "assembly" | "education" | "gender" | "employment" | "culture"
  showCategoryName?: boolean
}

// 컴포넌트를 memo로 감싸서 불필요한 리렌더링 방지
const DepartmentFeeds = memo(({ feeds, variant, showCategoryName = false }: DepartmentFeedsProps) => {
  return (
    <div className="p-4 space-y-2">
      <div className="space-y-2">
        {feeds.map((feed) => (
          <FeedItem key={feed.article_id} {...feed} variant={variant} showCategoryName={showCategoryName} />
        ))}
      </div>
    </div>
  )
})

// 컴포넌트 표시 이름 설정
DepartmentFeeds.displayName = "DepartmentFeeds"

export default DepartmentFeeds

