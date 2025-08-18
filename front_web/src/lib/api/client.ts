import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { getAccessToken, setAccessToken } from './tokenManager';

// 새로운 Access Token을 발급받기 위한 API 호출 함수
// 이 함수는 인터셉터 내부에서만 사용
const refreshAccessToken = async () => {
    try {
        // '/api/v1'은 apiClient의 baseURL에 이미 포함되어 있으므로, 그 뒤의 경로만 작성
        const response = await apiClient.post('/auth/refresh');
        const newAccessToken = response.data.data.access_token;
        
        if (newAccessToken) {
        setAccessToken(newAccessToken);
        return newAccessToken;
        }
    } catch (error) {
        console.error('Failed to refresh access token:', error);
        // 토큰 재발급 실패 시, 기존 토큰을 삭제하고 로그인 페이지로 리디렉션할 수 있음
        // 이 로직은 AuthContext에서 처리하는 것이 더 적합, 여기서는 에러를 throw
        setAccessToken(null);
        throw error;
    }
    };

// 1. Axios 인스턴스 생성
export const apiClient = axios.create({
  // .env.local 파일에 NEXT_PUBLIC_API_URL을 설정
  // 예시: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    
    baseURL: process.env.NEXT_PUBLIC_API_URL,
    //baseURL: '/api/v1',
  // 다른 서버로 쿠키를 보내기 위한 설정
    withCredentials: true,
});

// 재요청 로직을 위한 변수
let isRefreshing = false;
let failedQueue: { resolve: (token: string | null) => void; reject: (error: Error) => void; }[] = [];

const processQueue = (error: AxiosError | null, token: string | null = null) => {
    failedQueue.forEach(prom => {
        if (error) {
        prom.reject(error);
        } else {
        prom.resolve(token);
        }
    });
    failedQueue = [];
};

// 2. 요청(Request) 인터셉터 설정
apiClient.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        // /auth/refresh 요청에는 Access Token을 보내지 않음
        if (config.url === '/auth/refresh') {
        return config;
        }

        const token = getAccessToken();
        if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// 3. 응답(Response) 인터셉터 설정
apiClient.interceptors.response.use(
    (response) => {
        // 정상 응답은 그대로 반환
        return response;
    },
    async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
        
        // 401 에러가 아니거나, 재요청인 경우 그냥 에러를 반환
        if (error.response?.status !== 401 || originalRequest._retry) {
        return Promise.reject(error);
        }

        // '/auth/refresh' 요청 자체에서 401 에러가 발생한 경우 (Refresh Token 만료)
        if (originalRequest.url === '/auth/refresh') {
        console.error('Refresh token is expired or invalid.');
        // 여기서 로그인 페이지로 리디렉션하는 로직을 추가할 수 있음.
        // window.location.href = '/login';
        return Promise.reject(error);
        }

        if (isRefreshing) {
        return new Promise((resolve, reject) => {
            failedQueue.push({ resolve, reject });
        }).then(token => {
            if (originalRequest.headers) {
            originalRequest.headers['Authorization'] = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
        }).catch(err => {
            return Promise.reject(err);
        });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        try {
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
            if (originalRequest.headers) {
            originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
            }
            processQueue(null, newAccessToken);
            return apiClient(originalRequest);
        }
        } catch (refreshError: unknown) { 
        // refreshError: unknown아니고 refreshError이어도 암묵적으로는 unknown임
        // 'unknown' 형식의 인수는 'AxiosError<unknown, any> | null' 형식의 매개 변수에 할당될 수 없습니다. -> 수정된 부분. 
        // catch 블록에 있는 에러 변수(여기서는 refreshError)의 타입을 기본적으로 **unknown**으로 추론 
        // unknown 타입은 "이 변수가 어떤 타입인지 전혀 알 수 없다"는 의미로, 다른 타입의 변수에 직접 할당할 수 없음 -> 안전
        // 아 진짜 더럽게 깐깐하네
        if (axios.isAxiosError(refreshError)) {
            // axios.isAxiosError -> axios가 제공하는 타입 가드 함수
            // refreshError가 AxiosError임이 확인되었으므로 안전하게 전달 가능
            processQueue(refreshError, null);
        } else {
            // AxiosError가 아닌 다른 종류의 에러일 경우 (네트워크 오류 등)
            // 새로운 Error 객체를 만들어 전달하거나, null로 처리할 수 있음
            // 여기서는 null로 처리하여 큐에 있는 요청들이 무한 대기하지 않도록 함
            processQueue(new AxiosError('Unknown refresh error'), null);
        }
        return Promise.reject(refreshError);
        } finally {
        isRefreshing = false;
        }

        return Promise.reject(error);
    }
);