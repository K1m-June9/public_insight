import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AdminPopularKeyword } from "@/lib/types/admin/dashboard";

export function PopularKeywords({ keywords }: { keywords: AdminPopularKeyword[] }) {
  return (
    <Card>
      <CardHeader><CardTitle>인기 검색어</CardTitle></CardHeader>
      <CardContent>
        {keywords.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {keywords.map(kw => <Badge key={kw.keyword} variant="secondary">{kw.keyword} ({kw.count})</Badge>)}
          </div>
        ) : <p className="text-sm text-muted-foreground">검색 기록이 없습니다.</p>}
      </CardContent>
    </Card>
  );
}