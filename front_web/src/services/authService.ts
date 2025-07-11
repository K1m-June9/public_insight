import { apiClient } from '@/lib/api/client';
import { 
    LoginRequest, 
    TokenResponse,
    UserCreate,
    UserCheckIDRequest,
    UserCheckEmailRequest,
    ResetPasswordRequest,
    PasswordResetSubmitRequest
} from '@/lib/types/auth';
import { BaseResponse } from '@/lib/types/base';

/**
 * 사용자 로그인
 * @param credentials - 사용자 아이디와 비밀번호
 * @returns Promise<TokenResponse> - Access Token과 기타 정보
 */
export const login = async (credentials: LoginRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return response.data;
};

/**
 * 사용자 로그아웃
 * 백엔드에 로그아웃 요청을 보내 토큰을 무효화
 * @returns Promise<BaseResponse>
 */
export const logout = async (): Promise<BaseResponse> => {
  // 로그아웃 요청 시 body가 필요 없는 경우가 많지만,
  // 백엔드에서 쿠키 외에 body에서도 refresh_token을 받을 수 있게 되어있으므로 빈 객체를 보냄
    const response = await apiClient.post<BaseResponse>('/auth/logout', {});
    return response.data;
};

/**
 * 신규 사용자 회원가입
 * @param userData - 회원가입에 필요한 사용자 정보
 * @returns Promise<BaseResponse> - 성공 여부 응답
 */
export const register = async (userData: UserCreate): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/register', userData);
    return response.data;
};

/**
 * 사용자 아이디의 사용 가능 여부를 확인
 * @param params - 확인할 사용자 아이디
 * @returns Promise<BaseResponse> - 사용 가능 시 success: true
 */
export const checkUserIdAvailability = async (params: UserCheckIDRequest): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/check-id', params);
    return response.data;
}

/**
 * 이메일 인증 코드를 발송
 * 이건 아직 안쓰는거 아닌가? -> 아직 안씀
 * @param params - 인증 코드를 받을 이메일
 * @returns Promise<BaseResponse>
 */
export const sendVerificationCode = async (params: UserCheckEmailRequest): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/check-email/send', params);
    return response.data;
}

/**
 * 입력된 이메일 인증 코드를 검증
 * @param params - 이메일과 인증 코드
 * @returns Promise<BaseResponse>
 */
export const verifyEmailCode = async (params: { email: string; code: string }): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/check-email/verify', params);
    return response.data;
}

/**
 * 비밀번호 재설정 요청을 보냄 (이메일 발송)
 * @param params - 사용자 아이디와 이메일
 * @returns Promise<BaseResponse>
 */
export const requestPasswordReset = async (params: ResetPasswordRequest): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/reset-password-reset', params);
    return response.data;
}

/**
 * 비밀번호를 실제로 재설정
 * @param params - 재설정 토큰과 새로운 비밀번호
 * @returns Promise<BaseResponse>
 */
export const resetPassword = async (params: PasswordResetSubmitRequest): Promise<BaseResponse> => {
    const response = await apiClient.post<BaseResponse>('/auth/reset-password', params);
    return response.data;
}