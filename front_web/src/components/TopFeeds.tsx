import Link from "next/link"
import { ArrowUp, MessageSquare, Eye, ArrowDown } from "lucide-react"

interface TopFeed {
  id: number
  title: string
  views: number
  likes: number
  comments: number
  dislikes: number
  department: string
}

const departmentColors: { [key: string]: string } = {
  국회: "text-blue-600",
  교육부: "text-green-600",
  여성가족부: "text-purple-600",
  고용노동부: "text-amber-600",
  문화체육관광부: "text-orange-600",
}

interface TopFeedsProps {
  feeds: TopFeed[]
}

export default function TopFeeds({ feeds }: TopFeedsProps) {
  return (
    <div className="p-4 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 text-indigo-700">TOP N</h2>
      <ul className="space-y-4">
        {feeds.map((feed) => (
          <li
            key={feed.id}
            className="border border-indigo-100 rounded-lg overflow-hidden transition-all duration-300 ease-in-out hover:shadow-md"
          >
            <Link href={`/feed/${feed.id}`} className="block p-4 hover:bg-indigo-50">
              <h3 className="font-medium text-gray-900 mb-2">
                {feed.title}
                <span className={`ml-2 text-sm ${departmentColors[feed.department] || "text-gray-500"}`}>
                  {feed.department}
                </span>
              </h3>
              <div className="flex items-center text-sm text-gray-500 space-x-4">
                <span className="flex items-center">
                  <Eye className="w-4 h-4 mr-1" />
                  {feed.views.toLocaleString()}
                </span>
                <span className="flex items-center">
                  <ArrowUp className="w-4 h-4 mr-1" />
                  {feed.likes.toLocaleString()}
                </span>
                <span className="flex items-center">
                  <ArrowDown className="w-4 h-4 mr-1" />
                  {feed.dislikes.toLocaleString()}
                </span>
                <span className="flex items-center">
                  <MessageSquare className="w-4 h-4 mr-1" />
                  {feed.comments.toLocaleString()}
                </span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}

