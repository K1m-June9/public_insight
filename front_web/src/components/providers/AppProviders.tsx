//프로바이더를 위한 별도 파일
'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '@/contexts/AuthContext'; // app/layout.tsx에서 쓰던거 이쪽으로 옮겨옴, 레이아웃에서 AppProvider 사용
import { SearchProvider } from '@/contexts/SearchContext';

export default function AppProviders({ children }: { children: React.ReactNode }) {
    // QueryClient 인스턴스를 생성
    // 컴포넌트가 리렌더링되어도 인스턴스가 유지되도록 useState를 사용
    const [queryClient] = useState(() => new QueryClient());

    return (
        <QueryClientProvider client={queryClient}>
        <AuthProvider>
        <SearchProvider>
            {children}
        </SearchProvider>
        </AuthProvider>
        </QueryClientProvider>
    );
}