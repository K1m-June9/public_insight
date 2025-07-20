import Link from "next/link";
import { PinnedNoticeData } from "@/lib/types/notice";
import { formatDate } from "@/lib/utils/date";

// 1. Props 타입 정의
interface NoticesProps {
  data?: PinnedNoticeData;
}

// 2. 컴포넌트가 props를 받도록 수정
export function Notices({ data }: NoticesProps) {
  // 3. Mock 데이터를 props로 받은 데이터로 교체
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
                {/* formatDate 유틸리티 함수 사용 */}
                <span className="text-sm text-gray-500">{formatDate(notice.created_at)}</span>
              </div>
            </Link>
          </li>
        ))}
      </ul>
      <div className="mt-4 text-right">
        <Link href="/notice" className="text-sm text-gray-500 hover:text-gray-700">
          더보기 &gt;
        </Link>
      </div>
    </div>
  );
}