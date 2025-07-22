"use client";

import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { useStaticPageQuery } from "@/hooks/queries/useStaticPageQueries";
import { Button } from "@/components/ui/button";
import Header from "@/components/header";
import Footer from "@/components/footer";

function StaticPageContent({ slug }: { slug: string }) {
  const { data, isLoading, isError } = useStaticPageQuery(slug);
  
  if (isLoading) {
    return <div className="animate-pulse text-gray-500">로딩 중...</div>;
  }
  if (isError) {
    return <div className="text-red-500">콘텐츠를 불러오는 데 실패했습니다.</div>;
  }
  
  const content = data?.data.page.content || "<p>콘텐츠가 없습니다.</p>";

  return <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: content }} />;
}


export default function AboutPage() {
  const router = useRouter();

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center mb-6">
              <Button variant="ghost" onClick={() => router.back()} className="flex items-center gap-1">
                <ArrowLeft className="h-4 w-4" />
                뒤로가기
              </Button>
            </div>
            <div className="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
                <h1 className="text-3xl font-bold mb-8 text-center">프로젝트 소개</h1>
                <StaticPageContent slug="about" />
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}