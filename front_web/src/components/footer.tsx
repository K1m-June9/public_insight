import Link from "next/link"

export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-200 bg-white py-8">
      <div className="w-full px-4 md:px-6">
        <div className="flex flex-col items-center justify-center space-y-4 text-center">
          <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2 text-sm">
            <Link href="/about" className="text-gray-500 hover:text-gray-900">
              ▸ 프로젝트 소개
            </Link>
            <Link href="/notices" className="text-gray-500 hover:text-gray-900">
              ▸ 공지사항
            </Link>
            <Link href="/terms" className="text-gray-500 hover:text-gray-900">
              ▸ 이용약관
            </Link>
            <Link href="/privacy" className="text-gray-500 hover:text-gray-900">
              ▸ 개인정보처리방침
            </Link>
            <Link href="/youth-protection" className="text-gray-500 hover:text-gray-900">
              ▸ 청소년보호정책
            </Link>
          </nav>
          <p className="text-sm text-gray-500">Copyright ⓒ 2024 - 2025 Public Insight. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}
