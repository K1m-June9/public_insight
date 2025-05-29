import { NextResponse } from "next/server"
import type { FeedItem, FeedDetail } from "@/types/feed"

const feedsData: FeedDetail[] = [
  {
    article_id: 1,
    title: "신규 일자리 창출 정책 발표",
    summation: "정부가 청년 실업률 감소를 위한 새로운 일자리 창출 정책을 발표했습니다.",
    content:
      "정부는 오늘 청년 실업 문제 해결을 위한 종합 대책을 발표했습니다. 이 정책은 중소기업 지원 강화, 창업 생태계 활성화, 직업 교육 확대 등을 주요 내용으로 담고 있습니다. 정부 관계자는 '이번 정책으로 향후 5년간 약 50만 개의 새로운 일자리가 창출될 것으로 기대한다'고 밝혔습니다.",
    category_id: 4,
    published_at: "2024.03.15",
    author_id: "gov_official_1",
    Link_to_original_material: "https://www.government.go.kr/policy/jobs2024",
    view_count: 1500,
    organization_subcategory: "고용정책과",
    likes: 230,
    dislikes: 45,
  },
  {
    article_id: 2,
    title: "위헌적 비상계엄 선포를 통한 내란 행위의 진상규명을 위한 특별검사 후보추천위원회 제3차 회의 결과",
    summation:
      '대통령 및 대통령 권한대행이 특검후보자 추천을 의뢰하지 않고 있는 상황에 대해, 국회는 2024년 12월 10일 "위헌적 비상계엄 선포를 통한 내란 행위의 진상규명을 위한 특별검사의 수사요구안"을 의결한 이후 현재까지 대통령 및 대통령 권한대행 모두 특검후보자 추천을 의뢰하지 않고 있음에 따라 추천위원회가 법적인 임무를 수행하지 못하고 있는 상황에 강한 유감을 표했다.',
    content:
      '대통령 및 대통령 권한대행이 특검후보자 추천을 의뢰하지 않고 있는 상황에 대해, 국회는 2024년 12월 10일 "위헌적 비상계엄 선포를 통한 내란 행위의 진상규명을 위한 특별검사의 수사요구안"을 의결한 이후 현재까지 대통령 및 대통령 권한대행 모두 특검후보자 추천을 의뢰하지 않고 있음에 따라 추천위원회가 법적인 임무를 수행하지 못하고 있는 상황에 강한 유감을 표했다. ',
    category_id: 1,
    published_at: "2024.09.15",
    author_id: "gov_official_5",
    Link_to_original_material:
      "https://www.assembly.go.kr/portal/bbs/B0000051/view.do?nttId=3438343&menuNo=600101&sdate=&edate=&searchDtGbn=c0&pageUnit=10&pageIndex=1",
    view_count: 7500,
    organization_subcategory: "국회사무처",
    likes: 1230,
    dislikes: 945,
  },
  {
    article_id: 1,
    title: "국회, 새로운 법안 통과",
    summation: "오늘 국회에서는 중요한 법안이 통과되었습니다. 이 법안은 많은 국민들의 관심사였던...",
    content:
      "국회는 오늘 중요한 법안을 통과시켰습니다. 이 법안은 많은 국민들의 관심사였던 주제를 다루고 있으며, 향후 우리 사회에 큰 영향을 미칠 것으로 예상됩니다. 법안의 주요 내용은 다음과 같습니다: [법안 내용 상세 설명]",
    category_id: 1,
    published_at: "2024.03.15",
    author_id: "assembly_member_1",
    Link_to_original_material: "https://www.assembly.go.kr/portal/lawmaking/1",
    view_count: 5000,
    organization_subcategory: "법제사법위원회",
    likes: 1230,
    dislikes: 45,
  },
  {
    article_id: 11,
    title: "교육부, 새 학기 교육 정책 발표",
    summation: "교육부가 새 학기를 맞아 새로운 교육 정책을 발표했습니다. 주요 내용으로는...",
    content:
      "교육부는 새 학기를 맞아 혁신적인 교육 정책을 발표했습니다. 이 정책은 학생들의 창의성 증진과 미래 역량 강화에 초점을 맞추고 있습니다. 주요 내용은 다음과 같습니다: [정책 내용 상세 설명]",
    category_id: 2,
    published_at: "2024.03.15",
    author_id: "education_official_1",
    Link_to_original_material: "https://www.moe.go.kr/boardCnts/1",
    view_count: 3500,
    organization_subcategory: "교육정책과",
    likes: 890,
    dislikes: 30,
  },
  {
    article_id: 21,
    title: "여성가족부, 성평등 정책 추진 계획 발표",
    summation: "여성가족부가 올해의 성평등 정책 추진 계획을 발표했습니다. 주요 내용은...",
    content:
      "여성가족부는 올해의 성평등 정책 추진 계획을 발표했습니다. 이 계획은 직장 내 성차별 해소, 일-가정 양립 지원 강화, 여성의 사회 참여 확대 등을 주요 목표로 하고 있습니다. 구체적인 추진 방안은 다음과 같습니다: [계획 내용 상세 설명]",
    category_id: 3,
    published_at: "2024.03.15",
    author_id: "gender_equality_official_1",
    Link_to_original_material: "https://www.mogef.go.kr/nw/1",
    view_count: 2800,
    organization_subcategory: "여성정책과",
    likes: 750,
    dislikes: 25,
  },
  {
    article_id: 31,
    title: "고용노동부, 일자리 창출 방안 발표",
    summation: "고용노동부가 새로운 일자리 창출 방안을 발표했습니다. 주요 정책으로는...",
    content:
      "고용노동부는 청년 실업 해소와 중장년층 재취업 지원을 위한 새로운 일자리 창출 방안을 발표했습니다. 이 방안은 산업 구조 변화에 대응하는 직업 훈련 강화, 스타트업 지원 확대, 공공 부문 일자리 확충 등을 포함하고 있습니다. 구체적인 내용은 다음과 같습니다: [방안 내용 상세 설명]",
    category_id: 4,
    published_at: "2024.03.15",
    author_id: "employment_official_1",
    Link_to_original_material: "https://www.moel.go.kr/news/1",
    view_count: 4200,
    organization_subcategory: "고용정책과",
    likes: 980,
    dislikes: 40,
  },
  {
    article_id: 41,
    title: "문화체육관광부, 관광산업 활성화 대책 발표",
    summation: "문화체육관광부가 관광산업 활성화를 위한 새로운 대책을 발표했습니다. 주요 내용은...",
    content:
      "문화체육관광부는 코로나19 이후 침체된 관광산업을 활성화하기 위한 종합 대책을 발표했습니다. 이 대책은 국내 관광 활성화, 해외 관광객 유치 확대, 관광 인프라 개선 등을 주요 내용으로 담고 있습니다. 구체적인 추진 방안은 다음과 같습니다: [대책 내용 상세 설명]",
    category_id: 5,
    published_at: "2024.03.15",
    author_id: "culture_official_1",
    Link_to_original_material: "https://www.mcst.go.kr/kor/s_notice/1",
    view_count: 3800,
    organization_subcategory: "관광정책과",
    likes: 870,
    dislikes: 35,
  },
]

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const id = searchParams.get("id")

  if (id) {
    const feed = feedsData.find((feed) => feed.article_id === Number.parseInt(id))
    if (feed) {
      return NextResponse.json(feed)
    }
    return NextResponse.json({ error: "Feed not found" }, { status: 404 })
  }

  // id가 없으면 전체 목록 반환 (FeedItem 형식으로)
  const feedItems: FeedItem[] = feedsData.map(({ article_id, title, summation, category_id, published_at }) => ({
    article_id,
    title,
    summation,
    category_id,
    published_at,
  }))
  return NextResponse.json(feedItems)
}

