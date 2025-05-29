import { notFound } from "next/navigation"
import Image from "next/image"
import { Badge } from "@/components/ui/badge"
import Header from "@/components/Header"
import Footer from "@/components/Footer"
import { CalendarIcon, UserIcon } from "lucide-react"
import { format, parse } from "date-fns"

interface CapstonePost {
  id: string
  title: string
  tag: string
  author: string
  image: string
  content: string
  publishedAt: string
}

async function getCapstoneData(id: string): Promise<CapstonePost | undefined> {
  const capstonePosts = [
    {
      id: "1",
      title: "요약 및 키워드 추출",
      tag: "NLP",
      author: "Pumpkin",
      image: "/capstone1.jpg",
      content: `뢀`,
      publishedAt: "2024.03.15",
    },
    {
      id: "2",
      title: "AWS 클라우드",
      tag: "Cloud",
      author: "Bee",
      image: "/capstone2.jpg",
      content: `사용사용.
      
      주요 특징:
      1. 블록체인을 통한 데이터 무결성 보장
      2. 스마트 컨트랙트를 이용한 자동화된 인증 프로세스
      3. 학생, 교육기관, 기업 간의 효율적인 정보 공유
      
      프로젝트 결과, 데이터의 신뢰성이 향상되고 학생들의 경력 관리가 더욱 용이해졌습니다. 향후 이 시스템을 실제 교육 환경에 도입하여 그 효과를 검증할 계획입니다.`,
      publishedAt: "2024.02.20",
    },
    {
      id: "3",
      title: "React, tailwind css 사용",
      tag: "UX/UI",
      author: "관리자",
      image: "/capstone3.jpg",
      content: `새 학기를 맞아 AR 기술을 활용한 실시간 언어 번역 앱 개발 프로젝트 참여 학생을 모집합니다.
      
      프로젝트 개요:
      - AR (증강현실) 기술과 자연어 처리 기술을 결합하여 실시간으로 외국어 텍스트를 번역하고 AR로 표시하는 모바일 앱 개발
      - 사용 기술: Unity, ARCore, TensorFlow, Python
      
      모집 인원: 5명 (AR 개발 2명, 백엔드 개발 2명, UI/UX 디자인 1명)
      지원 자격: 관련 기술에 관심이 있는 3학년 이상 학부생
      지원 방법: 3월 30일까지 담당 교수에게 이메일로 지원서 제출
      
      많은 관심과 지원 바랍니다.`,
      publishedAt: "2024.03.10",
    },
  ]

  return capstonePosts.find((post) => post.id === id)
}

export default async function CapstonePage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  // params를 await로 처리한 후 id 속성에 접근
  const resolvedParams = await params
  const capstoneData = await getCapstoneData(resolvedParams.id)

  if (!capstoneData) {
    return notFound()
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        <article className="bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="relative h-64 sm:h-80 md:h-96">
            <Image
              src={capstoneData.image || "/placeholder.svg"}
              alt={capstoneData.title}
              fill
              style={{ objectFit: "cover" }}
              className="transition-opacity duration-300 hover:opacity-90"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute bottom-0 left-0 p-6 text-white">
              <Badge variant="secondary" className="mb-2">
                {capstoneData.tag}
              </Badge>
              <h1 className="text-3xl font-bold mb-2">{capstoneData.title}</h1>
              <div className="flex items-center text-sm space-x-4">
                <div className="flex items-center">
                  <UserIcon className="w-4 h-4 mr-1" />
                  <span>{capstoneData.author}</span>
                </div>
                <div className="flex items-center">
                  <CalendarIcon className="w-4 h-4 mr-1" />
                  <span>{format(parse(capstoneData.publishedAt, "yyyy.MM.dd", new Date()), "yyyy.MM.dd")}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="p-6">
            <div className="prose max-w-none">
              {capstoneData.content.split("\n").map((paragraph, index) => (
                <p key={index} className="mb-4 text-gray-700 leading-relaxed">
                  {paragraph}
                </p>
              ))}
            </div>
          </div>
        </article>
      </main>
      <Footer />
    </div>
  )
}

