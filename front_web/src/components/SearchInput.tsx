"use client";
import { type FormEvent, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Search } from "lucide-react";
import { useSearch } from "@/contexts/SearchContext";
import { Input } from "@/components/ui/input";

export function SearchInput() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { searchQuery, setSearchQuery } = useSearch();

  // URL의 'q' 파라미터를 읽어서 검색창 상태를 초기화/동기화
  useEffect(() => {
    const q = searchParams.get('q');
    if (q !== null) {
      setSearchQuery(q);
    }
  }, [searchParams, setSearchQuery]);

  const handleSearch = (e: FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      router.push(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="hidden md:flex md:w-1/3 lg:w-1/2 xl:w-1/3">
      <div className="relative w-full">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
        <Input type="search" placeholder="검색어를 입력하세요" className="pl-10 bg-input-background border-border" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
      </div>
    </form>
  );
}