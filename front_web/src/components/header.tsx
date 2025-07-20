"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Search, Bell, Shield } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useLogoutMutation } from "@/hooks/mutations/useAuthMutations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { UserRole } from "@/lib/types/base"; // UserRole enum 임포트

export default function Header() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState("");
  
  // 1. AuthContext와 커스텀 훅 사용
  const { user, isLoading } = useAuth();
  const { mutate: logout, isPending: isLoggingOut } = useLogoutMutation();

  const isLoggedIn = !!user; // user 객체의 존재 여부로 로그인 상태 판단

  // 검색 제출 처리
  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  // 마이페이지/관리자페이지 이동 처리
  const handleUserPageClick = () => {
    if (user?.role === UserRole.ADMIN || user?.role === UserRole.MODERATOR) {
      router.push("/admin"); // 관리자 페이지 경로로 수정 필요
    } else {
      router.push("/mypage"); // 마이페이지 경로로 수정 필요
    }
  };

  // 로딩 중에는 헤더의 일부만 간단히 보여줄 수 있습니다. (선택사항)
  if (isLoading) {
    return (
      <header className="sticky top-0 z-50 w-full border-b bg-white">
        <div className="w-full flex h-16 items-center justify-between px-4 md:px-6">
          <Link href="/" className="flex items-center">
            <span className="text-xl font-bold text-gray-900">PublicInsight</span>
          </Link>
          <div className="h-8 w-24 bg-gray-200 rounded-md animate-pulse" />
        </div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white">
      <div className="w-full flex h-16 items-center justify-between px-4 md:px-6">
        {/* 로고 */}
        <Link href="/" className="flex items-center">
          <span className="text-xl font-bold text-gray-900">PublicInsight</span>
        </Link>

        {/* 검색창 */}
        <form onSubmit={handleSearch} className="hidden md:flex md:w-1/3 lg:w-1/2 xl:w-1/3">
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
            <Input
              type="search"
              placeholder="검색어를 입력하세요"
              className="w-full pl-9 bg-gray-100 border-gray-300"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </form>

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
              <Button variant="ghost" onClick={() => router.push("/login")}>
                로그인
              </Button>

              {/* 회원가입 버튼 */}
              <Button variant="outline" onClick={() => router.push("/signup")}>
                회원가입
              </Button>
            </>
          )}
        </div>
      </div>
    </header>
  );
}