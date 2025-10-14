"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

// Kibana에서 복사한 iframe의 URL을 여기에 붙여넣습니다.
// 💡 보안 및 유지보수를 위해, 이 URL은 .env.local 파일에 정의하고
//    process.env.NEXT_PUBLIC_KIBANA_DASHBOARD_URL 과 같이 사용하는 것이 가장 좋습니다.
const KIBANA_DASHBOARD_URL = "http://localhost:5600/app/dashboards#/view/2bfbfac0-a35f-11f0-b956-2baa63284f8f?embed=true&_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-15m%2Cto%3Anow))&show-top-menu=true&show-query-input=true&show-time-filter=true";

export default function KibanaDashboard() {
  return (
    <Card className="w-full h-[80vh]">
      <CardHeader>
        <CardTitle>운영 대시보드</CardTitle>
        <CardDescription>
          시스템의 로그 데이터를 시각화하여 보여줍니다. 데이터는 Kibana에서 제공됩니다.
        </CardDescription>
      </CardHeader>
      <CardContent className="h-full pb-6">
        <iframe
          src={KIBANA_DASHBOARD_URL}
          className="w-full h-full border rounded-md"
          title="Kibana Dashboard"
        />
      </CardContent>
    </Card>
  );
}