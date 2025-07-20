"use client";

import React, { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Search } from "lucide-react";
import { useSearchQuery } from "@/hooks/queries/useSearchQueries";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";
import { formatDate } from "@/lib/utils/date";
import { SearchParams, SortOption, AggregationItem, SearchData } from "@/lib/types/search";
import Header from "@/components/header";
import Footer from "@/components/footer";

// URL 쿼리 파라미터를 파싱하고 상태를 관리하는 커스텀 훅
function useSearchState() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // URL에서 직접 상태를 읽어옴. 이 컴포넌트는 더 이상 자체적인 상태를 갖지 않음.
  const params: SearchParams = {
    q: searchParams.get("q") || undefined,
    organizations: searchParams.get("organizations") || undefined,
    categories: searchParams.get("categories") || undefined,
    types: searchParams.get("types") || undefined,
    sort: (searchParams.get("sort") as SortOption) || SortOption.RELEVANCE,
    page: Number(searchParams.get("page")) || 1,
  };

  const [localSearchQuery, setLocalSearchQuery] = useState(params.q || "");
  
  // --- 💡 오류 1 해결: updateSearch 함수 수정 ---
  const updateSearch = (newParams: Partial<SearchParams>) => {
    const current = new URLSearchParams(Array.from(searchParams.entries()));

    // 페이지 변경이 아닌 다른 모든 변경 시에는 페이지를 1로 리셋
    if (!('page' in newParams)) {
      current.set('page', '1');
    }

    Object.entries(newParams).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        current.set(key, String(value));
      } else {
        current.delete(key);
      }
    });

    router.push(`/search?${current.toString()}`);
  };

  return { params, localSearchQuery, setLocalSearchQuery, updateSearch };
}

// 필터 컴포넌트 (수정 없음)
function FilterSidebar({ aggregations, params, updateSearch }: { aggregations: SearchData['aggregations'], params: SearchParams, updateSearch: (p: Partial<SearchParams>) => void }) {
    const handleFilterChange = (filterType: 'organizations' | 'categories' | 'types', value: string) => {
        const currentFilters = params[filterType]?.split(',') || [];
        const newFilters = currentFilters.includes(value)
            ? currentFilters.filter(item => item !== value)
            : [...currentFilters, value];
        updateSearch({ [filterType]: newFilters.join(',') || undefined });
    };

    const renderFilterSection = (title: string, filterType: 'organizations' | 'categories' | 'types', items: AggregationItem[]) => (
        <AccordionItem value={filterType}>
            <AccordionTrigger className="text-sm font-medium">{title}</AccordionTrigger>
            <AccordionContent>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                    {items.map((item) => (
                        <div key={item.name} className="flex items-center space-x-2">
                            <Checkbox id={`${filterType}-${item.name}`} checked={params[filterType]?.includes(item.name)} onCheckedChange={() => handleFilterChange(filterType, item.name)} />
                            <label htmlFor={`${filterType}-${item.name}`} className="text-sm">{item.name} ({item.count})</label>
                        </div>
                    ))}
                </div>
            </AccordionContent>
        </AccordionItem>
    );

    return (
        <div className="md:w-1/4 lg:w-1/5">
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                <h2 className="font-semibold mb-4">상세 필터</h2>
                <Accordion type="multiple" defaultValue={['organizations', 'categories', 'types']}>
                    {renderFilterSection('기관(부)', 'organizations', aggregations.organizations)}
                    {renderFilterSection('카테고리', 'categories', aggregations.categories)}
                    {renderFilterSection('게시물 유형', 'types', aggregations.types)}
                </Accordion>
            </div>
        </div>
    );
}

// 메인 검색 페이지 컴포넌트
export default function SearchPage() {
  const { params, localSearchQuery, setLocalSearchQuery, updateSearch } = useSearchState();
  const { data: searchData, isLoading, isError } = useSearchQuery(params, { enabled: !!params.q });

  const results = searchData?.data.results || [];
  const pagination = searchData?.data.pagination;
  const aggregations = searchData?.data.aggregations;
  
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateSearch({ q: localSearchQuery });
  };
  
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <form onSubmit={handleSearchSubmit} className="flex gap-2 mb-6 max-w-2xl mx-auto">
            <div className="relative flex-grow"><Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" /><Input type="search" placeholder="검색어를 입력하세요" className="pl-10" value={localSearchQuery} onChange={(e) => setLocalSearchQuery(e.target.value)} /></div>
            <Button type="submit">검색</Button>
          </form>

          <div className="flex flex-col md:flex-row gap-8">
            {aggregations && <FilterSidebar aggregations={aggregations} params={params} updateSearch={updateSearch} />}
            
            <div className="flex-1">
              <div className="flex justify-between items-center mb-4">
                <div className="text-sm text-gray-600">
                  {isLoading ? "검색 중..." : `총 ${pagination?.total_count || 0}개의 결과`}
                </div>
                {/* --- 💡 오류 2 해결: 타입 단언 사용 --- */}
                <Select value={params.sort} onValueChange={(value) => updateSearch({ sort: value as SortOption })}>
                  <SelectTrigger className="w-[180px]"><SelectValue placeholder="정렬 기준" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="relevance">관련도순</SelectItem>
                    <SelectItem value="latest">최신순</SelectItem>
                    <SelectItem value="oldest">오래된순</SelectItem>
                    <SelectItem value="views">조회수순</SelectItem>
                    <SelectItem value="rating">별점순</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {/* ... (이하 렌더링 로직은 이전과 동일) ... */}
              {isLoading ? (<div className="text-center py-8">로딩 중...</div>)
              : isError ? (<div className="text-center py-8 text-red-500">검색 중 오류가 발생했습니다.</div>)
              : results.length === 0 ? (<div className="bg-white p-8 rounded-lg shadow-sm text-center"><p className="text-gray-500">검색 결과가 없습니다.</p></div>)
              : (
                <div className="space-y-4">
                  {results.map((feed) => (
                    <Link href={`/feed/${feed.id}`} key={feed.id} className="block">
                      <div className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                        <h3 className="font-medium text-lg mb-2" dangerouslySetInnerHTML={{ __html: feed.highlight.title || feed.title }} />
                        <p className="text-gray-600 mb-3 line-clamp-2" dangerouslySetInnerHTML={{ __html: feed.highlight.summary || feed.summary }} />
                        <div className="flex flex-wrap items-center gap-2 text-xs">
                          <Badge variant="outline">{feed.organization.name}</Badge>
                          <Badge variant="secondary">{feed.category.name}</Badge>
                          <span className="text-gray-500 ml-auto">{formatDate(feed.published_date)}</span>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
               {pagination && pagination.total_pages > 1 && (
                  <div className="flex justify-center mt-8 space-x-2">
                      {/* 페이지네이션 버튼 렌더링 */}
                      {Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map(pageNumber => (
                          <Button key={pageNumber} variant={pageNumber === pagination.current_page ? 'default' : 'outline'} size="icon" onClick={() => updateSearch({ page: pageNumber })}>
                              {pageNumber}
                          </Button>
                      ))}
                  </div>
              )}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}