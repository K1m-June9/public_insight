"use client";

import Link from "next/link";
import { Building, ExternalLink } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { OrganizationListData } from "@/lib/types/organization";

interface OrganizationListProps {
  chartData?: OrganizationListData;
}

export function OrganizationList({ chartData }: OrganizationListProps) {
  const organizations = chartData?.organizations || [];

  return (
    <Card className="bg-card border border-border rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow">
      <CardHeader className="p-0 mb-0">
        <div className="flex items-center space-x-2">
          <Building className="w-5 h-5 text-primary" />
          <CardTitle className="text-primary text-lg font-medium">기관별 자료 보유 현황</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="space-y-2">
          {organizations.map((org) => (
            <Link
              href={`/organization/${org.name}`}
              key={org.id}
              className="block p-3 rounded-md transition-colors group hover:bg-accent cursor-pointer"
            >
              <div className="flex items-center justify-between text-sm">
                <span className="text-foreground group-hover:text-primary transition-colors">
                  {org.name}
                </span>
                <div className="flex items-center space-x-2">
                  <span className="text-muted-foreground font-medium w-12 text-right">
                    {org.feed_count.toLocaleString()}건
                  </span>
                  <ExternalLink className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}