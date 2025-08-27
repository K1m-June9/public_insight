from app.F7_models.users import UserRole

#예시
admin_paths = {
    "/api/v1/admin": {UserRole.ADMIN}, 
    "/api/v1/moderate": {UserRole.ADMIN, UserRole.MODERATOR},
    # 필요에 따라 추가 경로와 역할 지정
    "/api/v1/admin/static-pages":{UserRole.ADMIN}, #관리자 정적 페이지 목록 조회
    "/api/v1/admin/feeds":{UserRole.ADMIN}, #피드 관리 페이지 목록 조회
    "/api/v1/admin/organization/list":{UserRole.ADMIN}, #원래 계획에 없던 거(관리자 피드 조회 시 기관 및 카테고리 확인을 위한)
    "/api/v1/admin/organizations": {UserRole.ADMIN},
    "/api/v1/admin/slider": {UserRole.ADMIN},
    "/api/v1/admin/users": {UserRole.ADMIN},
}

admin_regex_paths = {
}

admin_regex_paths = {

    # --- 사용자 관리 (User Management) ---
    # [목록] GET /api/v1/admin/users
    # '?' 쿼리 파라미터가 붙을 수 있으므로, 경로 끝($)을 명시하는 것이 안전합니다.
    r"^/api/v1/admin/users/?$": {UserRole.ADMIN},

    # [상세] GET /api/v1/admin/users/{user_id}
    # user_id는 문자열이므로, 슬래시(/)를 제외한 모든 문자를 허용합니다. ([^/]+)
    r"^/api/v1/admin/users/[^/]+/?$": {UserRole.ADMIN},
    
    # [역할 변경] PATCH /api/v1/admin/users/{id}/role
    # id는 숫자이므로, 숫자가 1번 이상 반복됨을 의미하는 \d+를 사용합니다.
    r"^/api/v1/admin/users/\d+/role/?$": {UserRole.ADMIN},
    
    # [상태 변경] PATCH /api/v1/admin/users/{id}/status
    r"^/api/v1/admin/users/\d+/status/?$": {UserRole.ADMIN},

    # [활동 로그 조회] GET /api/v1/admin/users/{user_id}/activities
    r"^/api/v1/admin/users/[^/]+/activities/?$": {UserRole.ADMIN},


    # --- 슬라이더 관리(Slider Management) ---
    # [목록] GET /api/v1/admin/sliders
    # [생성] POST /api/v1/admin/sliders
    # 목록 조회(GET)와 생성(POST)은 동일한 경로를 사용하므로 하나의 규칙으로 처리 가능
    r"^/api/v1/admin/slider/?$": {UserRole.ADMIN},
    
    # [상세] GET /api/v1/admin/sliders/{id}
    # [수정] PATCH /api/v1/admin/sliders/{id}
    # [삭제] DELETE /api/v1/admin/sliders/{id}
    # id는 숫자(\d+)이므로, 위 3개 API를 하나의 규칙으로 처리 가능
    r"^/api/v1/admin/slider/\d+/?$": {UserRole.ADMIN},

    # --- 공지사항 관리 (Notice Management) ---
    
    # [목록] GET /api/v1/admin/notices
    # [생성] POST /api/v1/admin/notices
    # 목록 조회(GET)와 생성(POST)은 동일한 경로를 사용하므로 하나의 규칙으로 처리
    r"^/api/v1/admin/notices/?$": {UserRole.ADMIN},
    
    # [상세] GET    /api/v1/admin/notices/{id}
    # [수정] PUT    /api/v1/admin/notices/{id}
    # [삭제] DELETE /api/v1/admin/notices/{id}
    # id는 숫자(\d+)이므로, 위 3개 API를 하나의 규칙으로 처리
    r"^/api/v1/admin/notices/\d+/?$": {UserRole.ADMIN},


    # --- 대시보드 관리 (Dashboard Management) ---
    # [조회] GET    /api/v1/admin/dashboard
    r"^/api/v1/admin/dashboard/?$": {UserRole.ADMIN},
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