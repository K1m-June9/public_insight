// 백엔드의 UserProfile 스키마에 해당
export interface User {
    user_id: string;
    nickname: string;
    email: string;
}

// 백엔드의 UserProfileResponse 스키마에 해당
export interface UserProfileResponse {
    success: boolean;
    data: {
        user: User;
    };
}