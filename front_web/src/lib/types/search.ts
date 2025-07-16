import { DataResponse } from './base';

// 정렬 옵션 Enum
export enum SortOption {
  RELEVANCE = "relevance",
  LATEST = "latest",
  OLDEST = "oldest",
  VIEWS = "views",
  RATING = "rating",
}

// 검색 API에 전달할 쿼리 파라미터 타입
export interface SearchParams {
  q?: string;
  organizations?: string; // 쉼표로 구분된 문자열
  categories?: string;
  types?: string;
  date_from?: string; // YYYY-MM-DD
  date_to?: string;
  sort?: SortOption;
  page?: number;
  limit?: number;
}

// 검색 결과 항목 타입
export interface SearchOrganization {
  id: number;
  name: string;
  logo_url: string;
}

export interface SearchCategory {
  id: number;
  name: string;
}

export interface SearchHighlight {
  title: string;
  summary: string;
}

export interface SearchResultItem {
  id: number;
  title: string;
  summary: string;
  organization: SearchOrganization;
  category: SearchCategory;
  type: string;
  published_date: string;
  view_count: number;
  average_rating: number;
  bookmark_count: number;
  url: string;
  highlight: SearchHighlight;
}

// 집계 데이터 타입
export interface AggregationItem {
  name: string;
  count: number;
}

export interface SearchAggregations {
  organizations: AggregationItem[];
  categories: AggregationItem[];
  types: AggregationItem[];
  date_ranges: AggregationItem[];
}

// 페이지네이션 타입
export interface SearchPagination {
    current_page: number;
    total_pages: number;
    total_count: number;
    limit: number;
    has_next: boolean;
    has_previous: boolean;
}

// 검색 응답 데이터 전체 구조
export interface SearchData {
  // query 정보는 프론트에서 이미 알고 있으므로, 응답 타입에서는 생략 가능
  results: SearchResultItem[];
  pagination: SearchPagination;
  aggregations: SearchAggregations;
  search_time: string;
}

export type SearchResponse = DataResponse<SearchData>;