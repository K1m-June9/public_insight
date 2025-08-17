import Link from "next/link"

export default function Footer() {
  return (
    <footer className="w-full bg-muted border-t border-border">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex flex-wrap justify-center items-center space-x-6 text-sm text-muted-foreground mb-4">
            <Link href="/about" className="hover:text-primary transition-colors">프로젝트 소개</Link>
            <Link href="/notice" className="hover:text-primary transition-colors">공지사항</Link>
            <Link href="/terms" className="hover:text-primary transition-colors">이용약관</Link>
            <Link href="/privacy" className="hover:text-primary transition-colors">개인정보처리방침</Link>
            <Link href="/youth-protection" className="hover:text-primary transition-colors">청소년보호정책</Link>
        </div>
        
        <div className="text-center text-xs text-muted-foreground">
          Copyright © 2024 - 2025 Public Insight. All rights reserved.
        </div>
      </div>
    </footer>
  );
}