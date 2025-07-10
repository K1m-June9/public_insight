import { BaseResponse, DataResponse } from './base';
import { UserRole } from './base'; // base.ts에 정의된 UserRole enum 사용

// =================================
// 1. 토큰 관련
// =================================

export interface TokenData {
    access_token: string;
    token_type: string;
    expires_in: number;
    refresh_token?: string; // 모바일 앱용이므로 optional
}

export interface TokenResponse extends BaseResponse {
    success: true;
    message: string;
    data: TokenData;
}

// =================================
// 2. 로그인 요청
// =================================

export interface LoginRequest {
    user_id: string;
    password: string;
}

// =================================
// 3. 회원가입 관련
// =================================

export interface UserCreate {
    user_id: string;
    email: string;
    password: string;
    terms_agreed: boolean;
    privacy_agreed: boolean;
    notification_agreed?: boolean;
}

// =================================
// 4. 아이디/이메일 중복 검사
// =================================

export interface UserCheckIDRequest {
    user_id: string;
}

export interface UserCheckEmailRequest {
    email: string;
}

// =================================
// 5. 아이디/비밀번호 찾기
// =================================

export interface FindIdResponse extends BaseResponse {
    success: true;
    masked_user_id: string;
}

export interface ResetPasswordRequest {
    user_id: string;
    email: string;
}

export interface PasswordResetSubmitRequest {
    token: string;
    new_password: string;
}