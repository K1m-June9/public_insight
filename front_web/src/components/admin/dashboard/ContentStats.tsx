import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AdminNoticeStats, AdminSliderStats, AdminOrganizationStat } from "@/lib/types/admin/dashboard";

const StatRow = ({ label, value }: { label: string, value: React.ReactNode }) => (
  <div className="flex items-center justify-between text-sm"><span className="text-muted-foreground">{label}</span><span className="font-medium">{value}</span></div>
);

export function ContentStats({ notices, sliders, orgs }: { notices: AdminNoticeStats; sliders: AdminSliderStats; orgs: AdminOrganizationStat[] }) {
  return (
    <Card>
      <CardHeader><CardTitle>콘텐츠 현황</CardTitle></CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">공지사항</h4>
          <StatRow label="활성" value={notices.active} />
          <StatRow label="고정" value={notices.pinned} />
        </div>
        <div>
          <h4 className="font-semibold mb-2">슬라이더</h4>
          <StatRow label="활성" value={sliders.active} />
          <StatRow label="비활성" value={sliders.inactive} />
        </div>
        <div>
          <h4 className="font-semibold mb-2">피드 보유 기관 TOP 5</h4>
          {orgs.map(org => <StatRow key={org.organization_name} label={org.organization_name} value={`${org.feed_count}개`} />)}
        </div>
      </CardContent>
    </Card>
  );
}