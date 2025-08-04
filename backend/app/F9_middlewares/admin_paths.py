from app.F7_models.users import UserRole

#예시
admin_paths = {
    "/api/v1/admin": {UserRole.ADMIN}, 
    "/api/v1/moderate": {UserRole.ADMIN, UserRole.MODERATOR},
    # 필요에 따라 추가 경로와 역할 지정
    "api/v1/admin/static-pages":{UserRole.ADMIN}, #관리자 정적 페이지 목록 조회
}

"""
[경로 지정 규칙]

1. 경로는 반드시 슬래시(/)로 시작
    ✅ 예: /api/v1/admin
    ❌ 예: api/v1/admin (잘못된 예시)

2. 경로는 '디렉토리'처럼 취급
    - 지정한 경로의 모든 하위 경로도 포함됩니다.
    ✅ 예: /api/v1/admin → /api/v1/admin/users, /api/v1/admin/settings 등 포함

3. 접근 허용 역할은 UserRole Enum에 정의된 값만 사용
    ✅ 예: {UserRole.ADMIN}
    ✅ 예: {UserRole.ADMIN, UserRole.MODERATOR}
    ❌ 예: {"admin"}, {"moderator"}

4. 너무 세부적인 경로는 피하고, 역할 기반 접근은 큰 기능 단위로 구분
    ✅ 예: /api/v1/admin  → 관리자 전체 영역
    ✅ 예: /api/v1/moderate → 콘텐츠 관리 등 중간 권한 영역

5. 필요 시 설명 주석 남기기
    예:
    "/api/v1/admin": {UserRole.ADMIN},  # 관리자 전용 기능
    
"""