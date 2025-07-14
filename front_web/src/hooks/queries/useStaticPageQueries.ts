// 아니 이건 도대체...

import { useQuery } from '@tanstack/react-query';
import { getStaticPage } from '@/services/staticPageService';

// 쿼리 키를 관리하기 위한 객체 (오타 방지 및 중앙 관리)
export const staticPageQueryKeys = {
    all: ['static-pages'] as const,
    detail: (slug: string) => [...staticPageQueryKeys.all, 'detail', slug] as const,
};

/**
 * 특정 slug를 가진 정적 페이지의 데이터를 조회하는 useQuery 훅
 * 
 * @param slug - 조회할 페이지의 slug (예: "about", "terms")
 * @param options - useQuery에 전달할 추가 옵션 (예: enabled, staleTime)
 * @returns {data, isLoading, isError, error, ...} - TanStack Query의 useQuery 반환 객체
 */
export const useStaticPageQuery = (slug: string, options?: { enabled?: boolean }) => {
    return useQuery({
        // 쿼리 키: 이 쿼리의 고유 식별자. slug가 다르면 다른 쿼리로 취급
        queryKey: staticPageQueryKeys.detail(slug),
        
        // 쿼리 함수: 실제 데이터를 가져오는 비동기 함수
        queryFn: () => getStaticPage(slug),
        
        // 옵션: 훅의 동작을 제어
        // enabled: 이 값이 true일 때만 쿼리가 자동으로 실행
        // slug가 유효할 때만 API를 호출하도록 설정 가능
        enabled: options?.enabled ?? !!slug, // slug가 존재할 때만 쿼리를 활성화

        // staleTime: 데이터가 '신선함'을 유지하는 시간 (밀리초 단위).
        // 이 시간 동안에는 데이터가 캐시에서 즉시 반환되며, 네트워크 요청을 보내지 않음
        // 정적 페이지는 자주 바뀌지 않으므로, staleTime을 길게 설정하여 불필요한 API 호출을 줄일 수 있음
        staleTime: 1000 * 60 * 5, // 5분
    });
};