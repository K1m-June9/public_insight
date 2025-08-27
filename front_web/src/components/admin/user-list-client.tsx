"use client";

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { useDebouncedCallback } from 'use-debounce';
import { useAdminUsersQuery } from '@/hooks/queries/useAdminUserQueries';
import { formatDate } from '@/lib/utils/date';
import { UserRole, UserStatus } from '@/lib/types/admin/user';

// UI Components
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Eye } from 'lucide-react';

export default function UserListClient({ searchParams }: { searchParams: { [key: string]: string | string[] | undefined } }) {
  const router = useRouter();
  const pathname = usePathname();
  const currentSearchParams = useSearchParams();

  const [filters, setFilters] = useState({
    page: Number(searchParams.page) || 1,
    search: (searchParams.search as string) || '',
    role: (searchParams.role as UserRole) || undefined,
    status: (searchParams.status as UserStatus) || undefined,
  });

  const { data: usersData, isLoading, isError } = useAdminUsersQuery({ ...filters, limit: 20 });
  const users = usersData?.data.users || [];
  const pagination = usersData?.data.pagination;
  const stats = usersData?.data.statistics;

  const updateURL = useDebouncedCallback((newFilters) => {
    const params = new URLSearchParams(currentSearchParams);
    Object.entries(newFilters).forEach(([key, value]) => {
      if (value) {
        params.set(key, String(value));
      } else {
        params.delete(key);
      }
    });
    router.replace(`${pathname}?${params.toString()}`);
  }, 300);

  useEffect(() => {
    setFilters({
      page: Number(searchParams.page) || 1,
      search: (searchParams.search as string) || '',
      role: (searchParams.role as UserRole) || undefined,
      status: (searchParams.status as UserStatus) || undefined,
    });
  }, [searchParams]);

  const handleFilterChange = (key: string, value: string) => {
    const newPage = key !== 'page' ? 1 : Number(value);
    const newFilters = { ...filters, [key]: value || undefined, page: newPage };
    updateURL(newFilters);
  };

  const handlePageChange = (newPage: number) => {
    if (newPage < 1 || (pagination && newPage > pagination.total_pages)) return;
    handleFilterChange('page', String(newPage));
  };
  
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">사용자 관리</h2>
      
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {Object.entries({
            '총 사용자': stats.total_users,
            '관리자': stats.by_role.admin,
            '활성 사용자': stats.by_status.active,
            '정지된 사용자': stats.by_status.suspended,
          }).map(([title, value]) => (
            <Card key={title}><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">{title}</CardTitle></CardHeader><CardContent><div className="text-2xl font-bold">{value}</div></CardContent></Card>
          ))}
        </div>
      )}

      <Card>
        <CardContent className="p-4 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <Input placeholder="사용자 ID, 닉네임, 이메일 검색..." defaultValue={filters.search} onChange={(e) => handleFilterChange('search', e.target.value)} className="max-w-sm" />
            <Select value={filters.role} onValueChange={(value) => handleFilterChange('role', value)}><SelectTrigger className="w-[180px]"><SelectValue placeholder="역할별 필터" /></SelectTrigger><SelectContent><SelectItem value="">모든 역할</SelectItem>{Object.values(UserRole).map(role => <SelectItem key={role} value={role}>{role}</SelectItem>)}</SelectContent></Select>
            <Select value={filters.status} onValueChange={(value) => handleFilterChange('status', value)}><SelectTrigger className="w-[180px]"><SelectValue placeholder="상태별 필터" /></SelectTrigger><SelectContent><SelectItem value="">모든 상태</SelectItem>{Object.values(UserStatus).map(status => <SelectItem key={status} value={status}>{status}</SelectItem>)}</SelectContent></Select>
          </div>
          <Table>
            <TableHeader><TableRow><TableHead>사용자 ID</TableHead><TableHead>닉네임</TableHead><TableHead>이메일</TableHead><TableHead>역할</TableHead><TableHead>상태</TableHead><TableHead>가입일</TableHead><TableHead className="text-right">작업</TableHead></TableRow></TableHeader>
            <TableBody>
              {isLoading ? (<TableRow><TableCell colSpan={7} className="text-center h-24">로딩 중...</TableCell></TableRow>)
              : isError ? (<TableRow><TableCell colSpan={7} className="text-center h-24 text-destructive">오류가 발생했습니다.</TableCell></TableRow>)
              : users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-mono">{user.user_id}</TableCell>
                    <TableCell className="font-medium">{user.nickname}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell><Badge variant={user.role === UserRole.ADMIN ? "default" : "secondary"}>{user.role}</Badge></TableCell>
                    <TableCell><Badge variant={user.status !== UserStatus.ACTIVE ? "destructive" : "outline"}>{user.status}</Badge></TableCell>
                    <TableCell>{formatDate(user.created_at)}</TableCell>
                    <TableCell className="text-right"><Button asChild variant="outline" size="sm"><Link href={`/admin/users/${user.user_id}`}><Eye className="w-4 h-4 mr-1" />상세보기</Link></Button></TableCell>
                  </TableRow>
                ))}
            </TableBody>
          </Table>
          
          {pagination && (
            <div className="flex items-center justify-center space-x-2 pt-4">
              <Button variant="outline" size="sm" onClick={() => handlePageChange(pagination.current_page - 1)} disabled={!pagination.has_previous}>이전</Button>
              <span>{pagination.current_page} / {pagination.total_pages}</span>
              <Button variant="outline" size="sm" onClick={() => handlePageChange(pagination.current_page + 1)} disabled={!pagination.has_next}>다음</Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}