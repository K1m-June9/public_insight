import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, FileText, Building, Eye, UserPlus } from "lucide-react";
import { AdminDashboardData } from "@/lib/types/admin/dashboard";

const overviewItems = (stats: AdminDashboardData) => [
  { title: "총 사용자", value: stats.total_users.toLocaleString(), icon: Users },
  { title: "총 피드", value: stats.total_feeds.toLocaleString(), icon: FileText },
  { title: "총 기관", value: stats.total_organizations.toLocaleString(), icon: Building },
  { title: "총 조회수", value: stats.total_views.toLocaleString(), icon: Eye },
  { title: "오늘 가입자", value: stats.today_signups.toLocaleString(), icon: UserPlus },
];

export function DashboardOverview({ stats }: { stats: AdminDashboardData }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {overviewItems(stats).map(item => (
        <Card key={item.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{item.title}</CardTitle>
            <item.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{item.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}