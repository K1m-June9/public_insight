import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AdminTopBookmarkedFeed, AdminTopRatedFeed } from "@/lib/types/admin/dashboard";
import { Star, Bookmark } from "lucide-react";

type TopFeedItem = AdminTopBookmarkedFeed | AdminTopRatedFeed;

export function TopFeeds({ title, type, data }: { title: string; type: 'bookmark' | 'rating'; data: TopFeedItem[] }) {
  return (
    <Card>
      <CardHeader><CardTitle className="flex items-center gap-2">{type === 'bookmark' ? <Bookmark className="w-4 h-4" /> : <Star className="w-4 h-4" />}{title}</CardTitle></CardHeader>
      <CardContent className="space-y-3">
        {data.length > 0 ? data.map(item => (
          <div key={item.id} className="text-sm">
            <p className="font-medium truncate">{item.title}</p>
            <div className="flex justify-between text-muted-foreground text-xs">
              <span>{item.organization_name}</span>
              {'bookmark_count' in item ? <span>{item.bookmark_count}회</span> : <span>★ {item.average_rating.toFixed(1)} ({item.rating_count}개)</span>}
            </div>
          </div>
        )) : <p className="text-sm text-muted-foreground">데이터가 없습니다.</p>}
      </CardContent>
    </Card>
  );
}