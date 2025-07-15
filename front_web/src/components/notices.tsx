import Link from "next/link";
import { PinnedNoticeData } from "@/lib/types/notice";
import { formatDate } from "@/lib/utils/date"; // 날짜 포맷팅 유틸 사용

interface NoticesProps {
  data?: PinnedNoticeData;
}

export function Notices({ data }: NoticesProps) {
  const notices = data?.notices || [];

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-4 text-gray-900">공지사항</h2>
      <ul className="space-y-3">
        {notices.map((notice) => (
          <li key={notice.id} className="border-b border-gray-100 pb-2">
            <Link href={`/notice/${notice.id}`} className="block hover:bg-gray-50 rounded p-1 -m-1 transition-colors">
              <div className="flex justify-between">
                <span className="font-medium">{notice.title}</span>
                <span className="text-sm text-gray-500">{notice.created_at}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
      <div className="mt-4 text-right">
        <Link href="/notices" className="text-sm text-gray-500 hover:text-gray-700">
          더보기 &gt;
        </Link>
      </div>
    </div>
  )
}
