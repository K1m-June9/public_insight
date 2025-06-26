# 정적 경로 처리용
exempt_paths = {
    "/health",
    "/docs",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
    "/api/v1/auth/register",
    "/api/v1/auth/check-id",
    "/api/v1/auth/check-email/send",
    "/api/v1/auth/check-email/verify",
    "/api/v1/sliders",
}

# 동적 경로 처리용
exempt_regex_paths = [
    r"^/api/v1/sliders/[1-9]\d*$",
    r"^/api/v1/static-pages/[a-z-]+$"
]




"""
[인증 예외 경로 지정 규칙 - exempt_paths]

1. 경로는 반드시 슬래시(/)로 시작
    ✅ 예: "/api/v1/auth/login"
    ❌ 예: "api/v1/auth/login" (슬래시 누락)

2. 완전한 경로만 등록 가능
    - 하위 경로를 자동 포함하지 않으므로, 필요한 모든 경로를 개별 등록
    ✅ 예: "/docs", "/openapi.json"
    ❌ 예: "/docs/*" (지원하지 않음)

3. 인증이 필요 없는 공개 API만 등록
    - 로그인, 토큰 갱신, 로그아웃 등 인증 미필요 엔드포인트에만 사용
    ✅ 예: /health, /api/v1/auth/login
    ❌ 예: /api/v1/users/me (인증 필요 → 제외 대상 아님)

4. 필요 시 설명 주석 남기기

"""
