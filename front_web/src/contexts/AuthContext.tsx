'use client'; // 이 컴포넌트는 클라이언트 측에서만 렌더링되어야 함을 명시

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types/user';
import { getMyProfile } from '@/services/userService';
import { getAccessToken, setAccessToken } from '@/lib/api/tokenManager';

// Context에 저장될 값의 타입을 정의합니다.
interface AuthContextType {
    user: User | null;
    setUser: (user: User | null) => void;
    isLoading: boolean;
    login: (accessToken: string, user: User) => void;
    logout: () => void;
}

// Context 생성 (초기값은 undefined)
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// AuthProvider 컴포넌트: 앱 전체를 감싸서 인증 상태를 제공합니다.
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true); // 앱 시작 시 인증 상태 확인 중임을 나타냄

    useEffect(() => {
        const checkAuthStatus = async () => {
        // apiClient의 인터셉터가 모든 것을 처리하므로, getMyProfile 호출만으로 충분.
        // 새로고침 시 메모리 토큰은 없지만, httpOnly 쿠키는 살아있음.
        // getMyProfile이 401을 반환하면, apiClient 인터셉터가 쿠키로 토큰 재발급을 시도하고,
        // 성공하면 새로운 토큰으로 getMyProfile을 재시도함.
        try {
            const profileResponse = await getMyProfile();
            if (profileResponse.success && profileResponse.data.user) {
            setUser(profileResponse.data.user);
            } else {
            // getMyProfile은 성공했으나 데이터가 없는 비정상 케이스
            setUser(null);
            }
        } catch (error) {
            // 재발급까지 실패한 경우, 최종적으로 로그아웃 상태가 됨.
            console.log("Authentication check/refresh failed. User is logged out.");
            setUser(null);
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

    const value = { user, setUser, isLoading, login, logout };

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