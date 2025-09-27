import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, setAccessToken } from './tokenManager';

let onRefreshFail: (() => void) | null = null;
export const setOnRefreshFail = (callback: () => void) => {
    onRefreshFail = callback;
};

// 🔹 refreshAccessToken 외부에서 호출 가능하도록 export
export const refreshAccessToken = async () => {
    try {
        const response = await apiClient.post('/auth/refresh', {});
        const newAccessToken = response.data.data.access_token;

        if (newAccessToken) {
            setAccessToken(newAccessToken);
            return newAccessToken;
        }
    } catch (error) {
        console.error('Failed to refresh access token:', error);
        setAccessToken(null);
        if (onRefreshFail) onRefreshFail(); // 🔹 실패 시 AuthContext logout 호출
        throw error;
    }
};

export const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    //baseURL: '/api/v1',
    //baseURL:'http://localhost:8002/api/v1', // ha_frontend 개발전용(으악)
  // 다른 서버로 쿠키를 보내기 위한 설정
    withCredentials: true,
});

let isRefreshing = false;
let failedQueue: { resolve: (token: string | null) => void; reject: (error: Error) => void; }[] = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) prom.reject(error);
        else prom.resolve(token);
    });
    failedQueue = [];
};

apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (config.url === '/auth/refresh') return config;
        const token = getAccessToken();
        if (token) config.headers['Authorization'] = `Bearer ${token}`;
        return config;
    },
    (error: AxiosError) => Promise.reject(error)
);

apiClient.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status !== 401 || originalRequest._retry) return Promise.reject(error);

        if (originalRequest.url === '/auth/refresh') return Promise.reject(error);

        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then(token => {
                if (originalRequest.headers) originalRequest.headers['Authorization'] = `Bearer ${token}`;
                return apiClient(originalRequest);
            }).catch(err => Promise.reject(err));
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
            const newAccessToken = await refreshAccessToken();
            if (newAccessToken && originalRequest.headers) {
                originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            }
            processQueue(null, newAccessToken);
            return apiClient(originalRequest);
        } catch (refreshError: unknown) {
            if (axios.isAxiosError(refreshError)) processQueue(refreshError, null);
            else processQueue(new AxiosError('Unknown refresh error'), null);
            return Promise.reject(refreshError);
        } finally {
            isRefreshing = false;
        }
    }
);
