import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { AxiosError } from 'axios';
import { setAccessToken } from '@/lib/api/tokenManager';
import { ErrorResponse } from '@/lib/types/base'; 
import { useAuth } from '@/contexts/AuthContext';
import {
    login as loginService,
    logout as logoutService,
    register as registerService,
    checkUserIdAvailability,
    sendVerificationCode
} from '@/services/authService';
import { getMyProfile } from '@/services/userService';
import { 
    LoginRequest, 
    UserCreate, 
    UserCheckIDRequest,
    UserCheckEmailRequest
} from '@/lib/types/auth';

/**
 * 로그인 처리를 위한 useMutation 훅
 */
export const useLoginMutation = () => {
    //const { login: setAuthContext } = useAuth();
    const { setUser } = useAuth(); 
    const router = useRouter();

    return useMutation({
        mutationFn: (credentials: LoginRequest) => loginService(credentials),
        onSuccess: async (data) => {
            const accessToken = data.data.access_token;
            if (accessToken) {
                // 1. 토큰을 받은 즉시 tokenManager에 저장합니다.
                setAccessToken(accessToken);

                try {
                    // 2. 이제 토큰이 저장되었으므로, getMyProfile은 성공적으로 토큰을 헤더에 추가합니다.
                    const profileResponse = await getMyProfile();
                    
                    if (profileResponse.success) {
                        // 3. 받아온 사용자 정보로 AuthContext의 user 상태를 업데이트합니다.
                        setUser(profileResponse.data.user);
                        
                        // 4. 메인 페이지로 리디렉션합니다.
                        router.push('/');
                    }
                } catch (profileError) {
                    // getMyProfile 실패 시 (예: 토큰은 유효하나 사용자가 비활성 상태) 처리
                    console.error("Failed to fetch profile after login:", profileError);
                    alert("로그인은 성공했으나 프로필 정보를 가져오는 데 실패했습니다.");
                    setAccessToken(null); // 저장했던 토큰 다시 비우기
                }
            }
        },
        onError: (error: AxiosError<ErrorResponse>) => {
            const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
            alert(message);
        },
    });
};

/**
 * 로그아웃 처리를 위한 useMutation 훅
 */
export const useLogoutMutation = () => {
    const { logout: clearAuthContext } = useAuth();
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: () => logoutService(),
        onSuccess: () => {
            clearAuthContext();
            queryClient.clear(); // 캐시된 모든 쿼리 데이터 삭제
            router.push('/');
        },
        onError: (error: AxiosError<ErrorResponse>) => {
            console.error('Logout failed:', error);
            // 에러가 발생하더라도 클라이언트 측 상태는 초기화
            clearAuthContext();
            queryClient.clear();
            router.push('/');
            const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
            alert(message);
        }
    });
};

/**
 * 회원가입 처리를 위한 useMutation 훅
 */
export const useRegisterMutation = () => {
    const router = useRouter();

    return useMutation({
        mutationFn: (userData: UserCreate) => registerService(userData),
        onSuccess: () => {
            alert('회원가입이 완료되었습니다. 로그인 페이지로 이동합니다.');
            router.push('/login'); // 실제 로그인 페이지 경로로 가정
        },
        onError: (error: AxiosError<ErrorResponse>) => {
            const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
            alert(message);
        }
    });
};

/**
 * 아이디 중복 확인을 위한 useMutation 훅
 * (데이터 조회지만, 버튼 클릭 시점에 실행되므로 mutation으로 관리하는 것이 편리)
 */
export const useCheckIdMutation = () => {
    return useMutation({
        mutationFn: (params: UserCheckIDRequest) => checkUserIdAvailability(params),
    });
};

/**
 * 이메일 인증 코드 발송을 위한 useMutation 훅
 */
export const useSendCodeMutation = () => {
    return useMutation({
        mutationFn: (params: UserCheckEmailRequest) => sendVerificationCode(params),
        onSuccess: () => {
            alert('인증코드가 발송되었습니다.');
        },
        onError: (error: AxiosError<ErrorResponse>) => {
            const message = error.response?.data?.error?.message || '오류가 발생했습니다.';
            alert(message);
        }
    });
};

// 다른 mutation 훅들도 비슷한 패턴으로 만들 수 있음
//useVerifyCodeMutation, useRequestPasswordResetMutation -> 현재는 X
