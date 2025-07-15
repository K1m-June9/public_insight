"use client";
import { Star, Eye, Bookmark } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import Link from "next/link";
import { Top5FeedData } from "@/lib/types/feed";

interface TopFeedsProps {
    data?: Top5FeedData;
}

export function TopFeeds({data}: TopFeedsProps) {
const topFeedsByRating = data?.top_rated || [];
  const topFeedsByViews = data?.most_viewed || [];
  const topFeedsByBookmarks = data?.most_bookmarked || [];


  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-900">TOP 5 피드</h2>
      <Tabs defaultValue="rating">
        <TabsList className="grid grid-cols-3 mb-4">
          <TabsTrigger value="rating" className="flex items-center gap-1">
            <Star className="h-4 w-4" />
            <span>별점순</span>
          </TabsTrigger>
          <TabsTrigger value="views" className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            <span>조회수순</span>
          </TabsTrigger>
          <TabsTrigger value="bookmarks" className="flex items-center gap-1">
            <Bookmark className="h-4 w-4" />
            <span>북마크순</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="rating">
          <ul className="space-y-3">
            {topFeedsByRating.map((feed) => (
              <li key={feed.id} className="border-b border-gray-100 pb-2">
                <Link href={`/feed/${feed.id}`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
                  <div className="flex justify-between">
                    <span className="font-medium">{feed.title}</span>
                    <span className="text-sm text-gray-500 flex items-center">
                      <Star className="h-3 w-3 mr-1 fill-current text-yellow-500" />
                      {feed.average_rating}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </TabsContent>

        <TabsContent value="views">
          <ul className="space-y-3">
            {topFeedsByViews.map((feed) => (
              <li key={feed.id} className="border-b border-gray-100 pb-2">
                <Link href={`/feed/${feed.id}`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
                  <div className="flex justify-between">
                    <span className="font-medium">{feed.title}</span>
                    <span className="text-sm text-gray-500 flex items-center">
                      <Eye className="h-3 w-3 mr-1" />
                      {feed.view_count.toLocaleString()}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </TabsContent>

        <TabsContent value="bookmarks">
          <ul className="space-y-3">
            {topFeedsByBookmarks.map((feed) => (
              <li key={feed.id} className="border-b border-gray-100 pb-2">
                <Link href={`/feed/${feed.id}`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
                  <div className="flex justify-between">
                    <span className="font-medium">{feed.title}</span>
                    <span className="text-sm text-gray-500 flex items-center">
                      <Bookmark className="h-3 w-3 mr-1" />
                      {feed.bookmark_count}
                    </span>
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        </TabsContent>
      </Tabs>
    </div>
  )
}
