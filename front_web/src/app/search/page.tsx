"use client";

import React, { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useSearchQuery } from "@/hooks/queries/useSearchQueries";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";
import { formatDate } from "@/lib/utils/date";
import { SearchParams, SortOption, AggregationItem, SearchData } from "@/lib/types/search";
import Header from "@/components/header";
import Footer from "@/components/footer";
import { useSearch } from "@/contexts/SearchContext";

// 필터 사이드바 컴포넌트
function FilterSidebar({ aggregations, params, updateSearch }: { aggregations: SearchData['aggregations'], params: SearchParams, updateSearch: (p: Partial<SearchParams>) => void }) {
    const handleFilterChange = (filterType: 'organizations' | 'categories' | 'types', value: string) => {
        const currentFilters = params[filterType]?.split(',').filter(Boolean) || [];
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
                    {(items || []).map((item) => (
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

// useSearchParams를 사용하는 모든 로직을 이 컴포넌트에 집중
function SearchResultArea() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setSearchQuery } = useSearch();

  const params: SearchParams = {
    q: searchParams.get("q") || undefined,
    organizations: searchParams.get("organizations") || undefined,
    categories: searchParams.get("categories") || undefined,
    types: searchParams.get("types") || undefined,
    sort: (searchParams.get("sort") as SortOption) || SortOption.RELEVANCE,
    page: Number(searchParams.get("page")) || 1,
  };

  useEffect(() => {
    if (params.q) {
      setSearchQuery(params.q);
    }
  }, [params.q, setSearchQuery]);

  const { data: searchData, isLoading, isError } = useSearchQuery(params, { enabled: !!params.q });

  const results = searchData?.data.results || [];
  const pagination = searchData?.data.pagination;
  const aggregations = searchData?.data.aggregations;

  const updateSearch = (newParams: Partial<SearchParams>) => {
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    if (!('page' in newParams)) {
      current.set('page', '1');
    }
    Object.entries(newParams).forEach(([key, value]) => {
      if (value) {
        current.set(key, String(value));
      } else {
        current.delete(key);
      }
    });
    router.push(`/search?${current.toString()}`);
  };

  return (
    <div className="flex flex-col md:flex-row gap-8">
      {aggregations && <FilterSidebar aggregations={aggregations} params={params} updateSearch={updateSearch} />}
      <div className="flex-1">
        <div className="flex justify-between items-center mb-4">
          <div className="text-sm text-gray-600">
            {isLoading ? "검색 중..." : `총 ${pagination?.total_count || 0}개의 결과`}
          </div>
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
        
        {isLoading ? (
          <div className="text-center py-8">로딩 중...</div>
        ) : isError ? (
          <div className="text-center py-8 text-red-500">검색 중 오류가 발생했습니다.</div>
        ) : results.length === 0 ? (
          <div className="bg-white p-8 rounded-lg shadow-sm text-center">
            <p className="text-gray-500">검색 결과가 없습니다.</p>
          </div>
        ) : (
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
            {Array.from({ length: pagination.total_pages }, (_, i) => i + 1).map(pageNumber => (
              <Button key={pageNumber} variant={pageNumber === pagination.current_page ? 'default' : 'outline'} size="icon" onClick={() => updateSearch({ page: pageNumber })}>
                {pageNumber}
              </Button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// 이 파일의 최종 내보내기(export)는 이 컴포넌트 하나
export default function SearchPage() {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow">
        <div className="container px-4 py-8 md:px-6">
          <div className="text-center mb-8">
             {/* 제목은 Header의 검색창과 SearchContext를 통해 동기화되므로 페이지 자체에서는 제목을 관리하지 않아도 됨 */}
             {/* 필요하다면 여기에 제목을 추가 */}
          </div>
          <Suspense fallback={<div className="text-center py-8">로딩 중...</div>}>
            <SearchResultArea />
          </Suspense>
        </div>
      </main>
      <Footer />
    </div>
  );
}