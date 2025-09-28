"use client";

import { Suspense } from 'react';
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import Image from 'next/image';

import { useLogoutMutation } from "@/hooks/mutations/useAuthMutations";
import { SearchInput } from "@/components/SearchInput"
// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuItem,
//   DropdownMenuTrigger,
// } from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { UserRole } from "@/lib/types/base"; // UserRole enum 임포트

export default function Header() {
  const router = useRouter();
  
  // 1. AuthContext와 커스텀 훅 사용
  const { user, isLoading } = useAuth();
  const { mutate: logout, isPending: isLoggingOut } = useLogoutMutation();

  const isLoggedIn = !!user; // user 객체의 존재 여부로 로그인 상태 판단

  // 마이페이지/관리자페이지 이동 처리
  const handleUserPageClick = () => {
    if (user?.role === UserRole.ADMIN || user?.role === UserRole.MODERATOR) {
      router.push("/admin/dashboard"); // 관리자 페이지 경로로 수정 필요
    } else {
      router.push("/mypage"); // 마이페이지 경로로 수정 필요
    }
  };

  // 로딩 중에는 헤더의 일부만 간단히 보여줄 수 있습니다. (선택사항)
  if (isLoading) {
    return (
      <header className="sticky top-0 z-50 w-full border-b bg-white">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900">PublicInsight</h1>
          </Link>
          <div className="h-8 w-24 bg-gray-200 rounded-md animate-pulse" />
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white">
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* 로고 */}
        <div className="text-xl font-semibold text-gray-900">
          <Link href="/" className="flex items-center space-x-2 text-primary"> {/* 💡 space-x-2 추가 */}
          {/* 💡 next/image 컴포넌트로 로고를 추가합니다. */}
          <Image 
            src="/logo.svg" // public 폴더 기준 경로
            alt="PublicInsight Logo"
            width={28} // 원하는 로고 너비 (픽셀)
            height={28} // 원하는 로고 높이 (픽셀)
            className="h-10 w-10" // Tailwind 클래스로도 크기 지정 가능
          />
        <h1 className="text-primary">PublicInsight</h1>
      </Link>
        </div>

        <Suspense fallback={<div className="hidden md:block h-8 w-1/3 bg-gray-100 rounded-md"></div>}>
          <SearchInput />
        </Suspense>

        {/* 로그인/회원가입 또는 사용자 메뉴 */}
        <div className="flex items-center gap-4">
          {isLoggedIn ? (
            <>
              {/* 알림 아이콘 (기능 비활성화) */}
              {/* 
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="relative">
                    <Bell className="h-5 w-5" />
                    <span className="absolute top-0 right-0 h-2 w-2 rounded-full bg-red-500"></span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuItem>새로운 알림이 없습니다</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              */}

              {/* 사용자 정보 */}
              <div className="flex items-center gap-2">
                {(user.role === UserRole.ADMIN || user.role === UserRole.MODERATOR) && (
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Shield className="h-3 w-3" />
                    관리자
                  </Badge>
                )}
                <Button variant="ghost" className="font-medium" onClick={handleUserPageClick}>
                  {user.nickname}
                </Button>
              </div>

              {/* 로그아웃 버튼 */}
              <Button variant="outline" onClick={() => logout()} disabled={isLoggingOut}>
                {isLoggingOut ? "로그아웃 중..." : "로그아웃"}
              </Button>
            </>
          ) : (
            <>
              {/* 로그인 버튼 */}
              <Button variant="ghost" className="text-foreground hover:text-primary" onClick={() => router.push("/login")}>
                로그인
              </Button>

              {/* 회원가입 버튼 */}
              <Button variant="default" className="bg-primary hover:bg-primary/90" onClick={() => router.push("/signup")}>
                회원가입
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}