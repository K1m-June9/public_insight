'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '@/lib/types/user';
import { getMyProfile } from '@/services/userService';
import { getAccessToken, setAccessToken } from '@/lib/api/tokenManager';
import { setOnRefreshFail, refreshAccessToken } from '@/lib/api/client'; // 🔹 refreshAccessToken import 추가

interface AuthContextType {
    user: User | null;
    setUser: (user: User | null) => void;
    isLoading: boolean;
    login: (accessToken: string, user: User) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const checkAuthStatus = async () => {
            const existingAccessToken = getAccessToken();

            if (!existingAccessToken) {
                setIsLoading(false);
                return;
            }

            try {
                const profileResponse = await getMyProfile();
                if (profileResponse.success && profileResponse.data.user) {
                    setUser(profileResponse.data.user);
                } else {
                    setUser(null);
                }
            } catch (error) {
                console.log("Authentication check/refresh failed. User is logged out.");
                setUser(null);
            } finally {
                setIsLoading(false);
            }
        };
        checkAuthStatus();

        // 🔹 인터셉터에서 refresh 실패 시 logout
        setOnRefreshFail(() => logout());

        // 🔹 토큰 만료 대비 주기적 refresh (예: 13분마다)
        const interval = setInterval(async () => {
            const token = getAccessToken();
            if (token) {
                try {
                    await refreshAccessToken();
                } catch (err) {
                    console.log("Periodic refresh failed:", err);
                }
            }
        }, 13 * 60 * 1000); // 🔹 주기: 4분 (예시, 필요시 백엔드 토큰 만료 시간보다 짧게 설정)

        return () => clearInterval(interval);
    }, []);

    const login = (accessToken: string, userData: User) => {
        setAccessToken(accessToken);
        setUser(userData);
    };

    const logout = () => {
        setAccessToken(null);
        setUser(null);
        // TODO: 백엔드 logout API 호출 가능
    };

    const value = { user, setUser, isLoading, login, logout };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = (): AuthContextType => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
