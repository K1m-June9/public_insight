import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AdminRecentActivity } from "@/lib/types/admin/dashboard";
import { ActivityType } from "@/lib/types/admin/user";
import { formatDate } from "@/lib/utils/date";
import { LogIn, LogOut, Eye, Bookmark, Star, Search, User } from "lucide-react";

const activityIcons: Record<ActivityType, React.ElementType> = {
  [ActivityType.LOGIN]: LogIn,
  [ActivityType.LOGOUT]: LogOut,
  [ActivityType.FEED_VIEW]: Eye,
  [ActivityType.FEED_BOOKMARK]: Bookmark,
  [ActivityType.FEED_RATING]: Star,
  [ActivityType.SEARCH]: Search,
  [ActivityType.PROFILE_UPDATE]: User,
};

export function RecentActivities({ activities }: { activities: AdminRecentActivity[] }) {
  return (
    <Card>
      <CardHeader><CardTitle>최근 활동</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        {activities.length > 0 ? activities.map(activity => {
          const Icon = activityIcons[activity.activity_type] || Search;
          return (
            <div key={activity.id} className="flex items-center gap-3 text-sm">
              <Icon className="w-4 h-4 text-muted-foreground" />
              <div className="flex-1">
                <span className="font-semibold">{activity.user_name}</span> 님이 {activity.activity_type} 활동을 했습니다.
              </div>
              <time className="text-xs text-muted-foreground">{formatDate(activity.created_at, 'YYYY-MM-DD HH:mm')}</time>
            </div>
          );
        }) : <p className="text-sm text-muted-foreground">최근 활동이 없습니다.</p>}
      </CardContent>
    </Card>
  );
}