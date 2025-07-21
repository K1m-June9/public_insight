// 이 파일은 Access Token을 안전하게 관리하기 위해 분리
// 브라우저 환경에서만 동작하도록 하여 서버 사이드 렌더링 시 에러를 방지

// Access Token을 저장할 변수 (메모리 저장)
let accessToken: string | null = null;

export const getAccessToken = (): string | null => {
  return accessToken;
};

export const setAccessToken = (token: string | null): void => {
  accessToken = token;
};