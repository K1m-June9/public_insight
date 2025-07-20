import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
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
    const { login: setAuthContext } = useAuth();
    const router = useRouter();

    return useMutation({
        mutationFn: (credentials: LoginRequest) => loginService(credentials),
        onSuccess: async (data) => {
            const accessToken = data.data.access_token;
            if (accessToken) {
                // `AuthContext`는 토큰을 직접 관리하지 않으므로, getMyProfile만 호출
                const profileResponse = await getMyProfile();
                if (profileResponse.success) {
                    // `AuthContext`의 login 함수를 호출하여 메모리에 토큰 저장 및 user 상태 업데이트
                    setAuthContext(accessToken, profileResponse.data.user);
                    router.push('/');
                }
            }
        },
        onError: (error) => {
            console.error('Login failed:', error);
            alert('아이디 또는 비밀번호가 올바르지 않습니다.');
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
        onError: (error) => {
            console.error('Logout failed:', error);
            // 에러가 발생하더라도 클라이언트 측 상태는 초기화
            clearAuthContext();
            queryClient.clear();
            router.push('/');
            alert('로그아웃 중 오류가 발생했습니다.');
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
        onError: (error: any) => {
            const message = error.response?.data?.error?.message || '회원가입 중 오류가 발생했습니다.';
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
        onError: (error: any) => {
            const message = error.response?.data?.error?.message || '인증코드 발송에 실패했습니다.';
            alert(message);
        }
    });
};

// 다른 mutation 훅들도 비슷한 패턴으로 만들 수 있음
//useVerifyCodeMutation, useRequestPasswordResetMutation -> 현재는 X