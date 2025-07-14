/**
 * 유효성 검사 관련 유틸리티 함수.
 * 백엔드(validator.py)의 규칙과 최대한 일치하도록 작성
 */

/**
 * 이메일 유효성 검사
 * @param email - 검사할 이메일
 * @returns 유효한 이메일인지 여부
 */
export function isValidEmail(email: string | null | undefined): boolean {
    if (!email) return false;
    const emailRegex = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    return emailRegex.test(email);
}

/**
 * 사용자 아이디 유효성 검사 (백엔드 규칙과 동일)
 * - 8~20자, 영문 소문자와 숫자만 허용, 숫자로 시작 금지
 * @param userId - 검사할 사용자 아이디
 * @returns 유효한 아이디인지 여부
 */
export function isValidUserId(userId: string | null | undefined): boolean {
    if (!userId) return false;
    const userIdRegex = /^[a-z][a-z0-9]{7,19}$/;
    return userIdRegex.test(userId);
}

/**
 * 비밀번호 유효성 검사 (백엔드 규칙과 동일)
 * - 10~25자, 영문 소문자/숫자/특수문자(!@$%^&*+~) 필수 포함, 특수문자로 시작 금지
 * @param password - 검사할 비밀번호
 * @returns 유효한 비밀번호인지 여부
 */
export function isValidPassword(password: string | null | undefined): boolean {
    if (!password) return false;

    // 길이 검사
    if (password.length < 10 || password.length > 25) return false;
    
    // 허용 문자 외 다른 문자 포함 여부 검사
    if (/[^a-z0-9!@$%^&*+~]/.test(password)) return false;

    // 필수 문자 포함 여부 검사
    const hasLetter = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);
    const hasSpecial = /[!@$%^&*+~]/.test(password);
    if (!hasLetter || !hasNumber || !hasSpecial) return false;

    // 특수문자로 시작하는지 검사
    if (/^[!@$%^&*+~]/.test(password)) return false;

    return true;
}

/**
 * 닉네임 유효성 검사 (백엔드 규칙과 동일)
 * - 2~12자, 한글/영문/숫자만 허용, 공백/이모지/특수문자 금지
 * @param nickname - 검사할 닉네임
 * @returns 유효한 닉네임인지 여부
 */
export function isValidNickname(nickname: string | null | undefined): boolean {
    if (!nickname) return false;
    
    // 길이 검사
    if (nickname.length < 2 || nickname.length > 12) return false;
    
    // 허용 문자(한글, 영문, 숫자) 외 다른 문자 포함 여부 검사
    const nicknameRegex = /^[가-힣a-zA-Z0-9]+$/;
    if (!nicknameRegex.test(nickname)) return false;

    // 금지 단어 검사 (백엔드와 동일하게)
    const forbiddenWords = ["운영자", "admin", "중재자", "moderator"];
    const lowered = nickname.toLowerCase();
    if (forbiddenWords.some(word => lowered.includes(word))) return false;

    return true;
}


// ==========================================================
// 프론트엔드에서만 사용되는 유효성 검사 함수들 (마코v0 에서 쓰던거)
// ==========================================================

/**
 * 빈 값 검사 (null, undefined, 빈 문자열)
 * @param value - 검사할 값
 * @returns 빈 값인지 여부
 */
export function isEmpty(value: any): boolean {
    return value === null || value === undefined || value === '';
}

/**
 * 필수 입력값 검사
 * @param value - 검사할 값
 * @returns 필수 입력값이 있는지 여부
 */
export function isRequired(value: any): boolean {
    return !isEmpty(value);
}