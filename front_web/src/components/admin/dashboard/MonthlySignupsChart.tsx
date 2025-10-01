"use client";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AdminDailySignupStat } from "@/lib/types/admin/dashboard";

export function MonthlySignupsChart({ data }: { data: AdminDailySignupStat[] }) {
  const formattedData = data.map(item => ({
    ...item,
    // YYYY-MM-DD -> MM/DD
    date: item.date.substring(5).replace('-', '/'),
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>일별 가입자 추이</CardTitle>
        <CardDescription>최근 90일간의 일별 가입자 수입니다.</CardDescription>
      </CardHeader>
      <CardContent className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={formattedData} margin={{ top: 5, right: 20, left: -10, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip />
            <Line type="monotone" dataKey="count" stroke="hsl(var(--primary))" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 8 }} />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}