"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { UserRole } from '@/lib/types/base'; // UserRole의 위치에 맞게 수정

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // 로딩이 끝나고, 유저 정보가 없거나 권한이 없는 경우에만 리디렉션
    if (!isLoading && (!user || (user.role !== UserRole.ADMIN && user.role !== UserRole.MODERATOR))) {
      router.replace('/');
    }
  }, [user, isLoading, router]); // 의존성 배열에 user, isLoading, router 추가

  // 로딩 중이거나 권한이 없는 상태에서는 로딩 화면을 보여줌
  if (isLoading || !user || (user.role !== UserRole.ADMIN && user.role !== UserRole.MODERATOR)) {
    return <div className="flex h-screen items-center justify-center">권한 확인 중...</div>;
  }

  // 모든 조건을 통과하면, 자식 컴포넌트(실제 관리자 페이지 레이아웃)를 렌더링
  return <>{children}</>;
}