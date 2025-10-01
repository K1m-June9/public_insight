// 이 파일은 Access Token을 안전하게 관리하기 위해 분리
// 브라우저 환경에서만 동작하도록 하여 서버 사이드 렌더링 시 에러를 방지

const ACCESS_TOKEN_KEY = 'access_token'; // 로컬 스토리지에 저장될 키 이름

export const getAccessToken = (): string | null => {
  // 로컬 스토리지에서 Access Token을 가져옴
  if (typeof window !== 'undefined') { // 브라우저 환경인지 확인
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }
  return null;
};

export const setAccessToken = (token: string | null): void => {
  // 로컬 스토리지에 Access Token을 저장하거나 제거함
  if (typeof window !== 'undefined') { // 브라우저 환경인지 확인
    if (token) {
      localStorage.setItem(ACCESS_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(ACCESS_TOKEN_KEY);
    }
  }
};

// 로그아웃 시 토큰 제거를 위한 추가 함수 (필요 시)
export const clearTokens = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    // Refresh Token이 HttpOnly 쿠키라면, 서버의 /auth/logout API 호출로 쿠키가 제거됨.
    // 클라이언트에서 직접 쿠키를 제거하는 것은 일반적으로 HttpOnly 쿠키에 대해 불가능함.
    // 만약 Refresh Token이 HttpOnly 쿠키가 아니라 일반 쿠키라면 아래와 같이 제거 가능
    // document.cookie = 'refreshToken=; Max-Age=0; path=/;';
  }
};