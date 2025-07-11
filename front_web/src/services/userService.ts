import { apiClient } from '@/lib/api/client';
import { setAccessToken } from '@/lib/api/tokenManager';
import { 
    UserProfileResponse,
    UserRatingListResponse,
    UserBookmarkListResponse,
} from '@/lib/types/user';
import { BaseResponse } from '@/lib/types/base';

// =================================
// 프로필 관련
// =================================

/**
* '내 정보 조회' API를 호출하여 현재 로그인된 사용자 정보를 가져옴
* @returns Promise<UserProfileResponse>
*/
export const getMyProfile = async (): Promise<UserProfileResponse> => {
    try {
        const response = await apiClient.get<UserProfileResponse>('/users/me');
        return response.data;
    } catch (error) {
        setAccessToken(null);
        console.error('Failed to get user profile:', error);
        throw error;
    }
};

/**
* 사용자 닉네임을 변경
* @param nickname - 새로운 닉네임
* @returns Promise<UserProfileResponse> - 업데이트된 프로필 정보
*/
export const updateNickname = async (nickname: string): Promise<UserProfileResponse> => {
    const response = await apiClient.patch<UserProfileResponse>('/users/profile/nickname', { nickname });
    return response.data;
};

/**
* 사용자 비밀번호를 변경
* @param params - 현재 비밀번호와 새로운 비밀번호
* @returns Promise<BaseResponse>
*/
export const updatePassword = async (params: { current_password: string; new_password: string }): Promise<BaseResponse> => {
    const response = await apiClient.put<BaseResponse>('/users/password', params);
    return response.data;
};


// =================================
// 별점 및 북마크 목록 조회
// =================================

interface PaginationParams {
    page?: number;
    limit?: number;
}

/**
* 현재 로그인한 사용자가 매긴 별점 목록을 조회합니다.
* @param params - 페이지네이션 파라미터 (page, limit)
* @returns Promise<UserRatingListResponse>
*/
export const getMyRatings = async (params: PaginationParams): Promise<UserRatingListResponse> => {
    const response = await apiClient.get<UserRatingListResponse>('/users/ratings', { params });
    return response.data;
};

/**
* 현재 로그인한 사용자의 북마크 목록을 조회합니다.
* @param params - 페이지네이션 파라미터 (page, limit)
* @returns Promise<UserBookmarkListResponse>
*/
export const getMyBookmarks = async (params: PaginationParams): Promise<UserBookmarkListResponse> => {
    const response = await apiClient.get<UserBookmarkListResponse>('/users/bookmarks', { params });
    return response.data;
};