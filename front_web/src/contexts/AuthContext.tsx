// 파일 위치: front_web/src/contexts/AuthContext.tsx

'use client'; // 이 컴포넌트는 클라이언트 측에서만 렌더링되어야 함을 명시합니다.

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types/user';
import { getMyProfile } from '@/services/userService';
import { getAccessToken, setAccessToken } from '@/lib/api/tokenManager';

// Context에 저장될 값의 타입을 정의합니다.
interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (accessToken: string, user: User) => void;
    logout: () => void;
}

// Context 생성 (초기값은 undefined)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider 컴포넌트: 앱 전체를 감싸서 인증 상태를 제공합니다.
export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true); // 앱 시작 시 인증 상태 확인 중임을 나타냄

    useEffect(() => {
        const checkAuthStatus = async () => {
        // Access Token이 없으면 확인할 필요도 없이 비로그인 상태.
        if (!getAccessToken()) {
            setIsLoading(false);
            return;
        }
        
        try {
            const response = await getMyProfile();
            if (response.success && response.data.user) {
            setUser(response.data.user);
            } else {
            // API 호출은 성공했으나, 데이터가 없는 경우 (이론상 발생하기 어려움)
            setUser(null);
            setAccessToken(null); // 토큰도 비워줍니다.
            }
        } catch (error) {
            console.log('Authentication check failed, user is not logged in.');
            setUser(null);
            // getMyProfile 내부에서 이미 토큰을 비웠을 것입니다.
        } finally {
            setIsLoading(false);
        }
        };

        checkAuthStatus();
    }, []);

    // 로그인 처리 함수
    const login = (accessToken: string, userData: User) => {
        setAccessToken(accessToken);
        setUser(userData);
    };

    // 로그아웃 처리 함수
    const logout = () => {
        // 실제 로그아웃 API 호출은 서비스 파일에서 처리하고,
        // 여기서는 클라이언트 측 상태만 변경합니다.
        setAccessToken(null);
        setUser(null);
        // TODO: 백엔드의 /auth/logout API 호출 로직 추가 필요
        // 예: authService.logout();
    };

    const value = { user, isLoading, login, logout };

    return (
        <AuthContext.Provider value={value}>
        {children}
        </AuthContext.Provider>
    );
};

// useAuth 훅: 컴포넌트에서 쉽게 AuthContext 값에 접근할 수 있도록 합니다.
export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};