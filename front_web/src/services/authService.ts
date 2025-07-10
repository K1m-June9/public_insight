import { apiClient } from '@/lib/api/client';
import { setAccessToken } from '@/lib/api/tokenManager';
import { UserProfileResponse } from '@/lib/types/user';

/**
* '내 정보 조회' API를 호출하여 현재 로그인된 사용자 정보를 가져옴
* API - GET /users/me
* @returns Promise<UserProfileResponse>
*/
export const getMyProfile = async (): Promise<UserProfileResponse> => {
    try {
        const response = await apiClient.get<UserProfileResponse>('/users/me');
        return response.data;
    } catch (error) {
        // getMyProfile 실패 시, Access Token이 유효하지 않다는 의미일 수 있음.
        // 토큰을 비워주는 로직을 추가.
        setAccessToken(null);
        console.error('Failed to get user profile:', error);
        // 에러를 다시 던져서 호출한 쪽에서 처리할 수 있도록 함.
        throw error;
    }
};