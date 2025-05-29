import Link from 'next/link'

export default function Footer() {
  return (
    <footer className="bg-gray-100 p-4">
      <div className="flex justify-center space-x-4 text-sm">
        <Link href="/about" className="text-gray-600">프로젝트 소개</Link>
        <span className="text-gray-300">|</span>
        <Link href="/terms" className="text-gray-600">고객 지원</Link>
        <span className="text-gray-300">|</span>
        <Link href="/privacy" className="text-gray-600">이용 안내</Link>
        <span className="text-gray-300">|</span>
        <Link href="/legal" className="text-gray-600">법적 정보</Link>
      </div>
    </footer>
  )
}

