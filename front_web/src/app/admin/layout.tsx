"use client";

import { useRouter } from "next/navigation";
import {useEffect} from "react"
import Link from "next/link";
import { BarChart3, Sliders, Megaphone, FileEdit, Building, Users, FileText } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { UserRole } from "@/lib/types/base";

// 1. 네비게이션 아이템 데이터
const navItems = [
  { href: "/admin", icon: BarChart3, label: "대시보드" },
  { href: "/admin/static-pages", icon: FileEdit, label: "정적 페이지" },
  { href: "/admin/sliders", icon: Sliders, label: "슬라이더" },
  { href: "/admin/notices", icon: Megaphone, label: "공지사항" },
  { href: "/admin/organizations", icon: Building, label: "기관/카테고리" },
  { href: "/admin/feeds", icon: FileText, label: "피드 관리" },
  { href: "/admin/users", icon: Users, label: "사용자 관리" },
];

// 2. 사이드바 컴포넌트
function AdminSidebar() {
  return (
    <aside className="w-64 flex-shrink-0 border-r bg-gray-100/50 p-4">
      <nav className="flex flex-col space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.label}
            href={item.href}
            className="flex items-center gap-3 rounded-lg px-3 py-2 text-gray-700 transition-all hover:bg-gray-200/70"
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

// 3. 관리자 페이지 전용 레이아웃
export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">권한 확인 중...</div>;
  }

  // 관리자가 아니면 메인 페이지로 리디렉션
  if (!user || (user.role !== UserRole.ADMIN && user.role !== UserRole.MODERATOR)) {
    // router.replace('/')는 서버 컴포넌트에서 직접 사용 불가하므로, 클라이언트 측에서 처리
    useEffect(() => {
      router.replace('/');
    }, [router]);
    return null; // 리디렉션 중에는 아무것도 렌더링하지 않음
  }
  
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1">
        <AdminSidebar />
        <main className="flex-1 p-8 bg-gray-50">
          {children}
        </main>
      </div>
      <Footer />
    </div>
  );
}