import CapstoneSlider from "./CapstoneSlider"
import FeedItem from "./FeedItem"
import type { FeedItem as FeedItemType } from "../types/feed" // type 키워드 추가

interface ContentCardsProps {
  feeds: FeedItemType[] // 타입으로 명시적 사용
}

export default function ContentCards({ feeds }: ContentCardsProps) {
  return (
    <div className="p-4 space-y-4">
      <CapstoneSlider />
      <div className="space-y-4">
        {feeds.map((feed) => (
          <FeedItem key={feed.article_id} {...feed} />
        ))}
      </div>
    </div>
  )
}

