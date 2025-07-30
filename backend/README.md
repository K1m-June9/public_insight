[폴더구조]
SU_DEV/
backend/
├── app/    
│   ├── alembic
│   ├── alembic.ini
│   │                   
│   ├── F1_routers/                
│   │   ├── v1/                   
│   │   │   ├── admin/
│   │   │   ├── api.py
│   │   │   ├── auth.py
│   │   │   ├── test.py         # 참고용
│   │ 
│   ├── F2_services/                
│   │   ├── auth.py
│   │
│   ├── F3_repositories/  
│   │   ├── auth.py          
│   │
│   ├── F4_utils/    
│   │   ├── client.py                
│   │   ├── cookie.py
│   │   ├── device.py
│   │   ├── email.py
│   │
│   ├── F5_core/                    
│   │   ├── config.py              
│   │   ├── dependencies.py
│   │   ├── logger.py           # 진행 중
│   │   ├── redis.py
│   │   ├── security.py
│   │
│   ├── F6_schemas/                  
│   │   ├── base.py
│   │   ├── auth.py
│   │
│   ├── F7_models/                  
│   │   ├── users.py
│   │   ├── refresh_token.py
│   │
│   ├── F8_database/            
│   │   ├── connection.py          
│   │   ├── session.py            
│   │ 
│   ├── F9_middlewares/      
│   │   ├── admin_paths.py                      # 경로 등록
│   │   ├── exempt_paths.py                     # 경로 등록
│   │   ├── jwt_bearer_middleware.py
│   │ 
│   ├── F10_task/          
│   │   ├── token_cleanup.py    # 진행 중
│   │ 
│   ├── F11_tests/ 
│   │   ├── auth/
│   │   │   ├── login_test.py
│   │   │   ├── refresh_test.py
│   │   │   ├── logout_test.py
│   │   │   ├── middleware_test.py
│   │   │
│   │   ├── reports/
│   │   │   ├── auth/
│   │   │   │   ├── login_test.html
│   │   │   │   ├── refresh_test.html
│   │   │   │   ├── logout_test.html
│   │   │   │   ├── middleware_test.py
│   │   │
│   │   ├── conftest.py
│   │
│   ├── .env
│   ├── main.py    
│   ├── pytest.ini
│   └── security.log    # 임시            
│  
├── venv/ 
├── Dockerfile    
├── README.md                  
├── requirements.txt                

[설명]
{1} 폴더명 앞에 숫자를 붙인 이유(예: F1_routers): 
        1. 정렬 안정성 : VSCode와 GitHub에서 의도한 순서로 폴더가 정렬되므로 빠르게 구조 파악 가능
        2. 가독성 향상 : 각 폴더의 역할이 한눈에 들어옴       
        3. 논리적 계층 구조 표현 : 라우터 -> 서비스 -> 레파지토리 -> DB처럼 상하계층 구조를 숫자로 표현 가능
        4. F1~F4 : 주 개발폴더



{2} 클래스, 함수 이름
        - 함수 이름 : user_register 함수
        - 클래스 이름 : UserRegister 클래스



{3} 필수 사항
1️⃣ verify_active_user 필수 적용 규칙
- JWT 미들웨어는 인증만 -> 상태는 라우터에서 체크
- Depends(verify_active_user)로 역할/상태 검증
- 미들웨어에서 I/O를 최소화, 라우터에서 DB 접근
[예시]
@router.get("/ping")
async def ping_active_user(current_user: User = Depends(verify_active_user)):
pass

2️⃣ F9_middlewares 경로 정의하기
[현재]
admin_paths.py: 관리자 경로 정의                
exempt_paths.py: 인증 제외 경로 정의

- 추후 관리를 위해 더 확장할 수 있음
- 상세한 사항은 파일 안에 기입되어 있음

[나중에(예시)]
public_paths.py: 로그인 없이 접근 가능한 공개 경로 정의
user_paths.py: 일반 사용자 전용 경로 정의

3️⃣ .env 환경에 맞게 수정하기
IS_LOCAL=true   # 👉 로컬 : pytest
IS_LOCAL=false  # 👉 도커 : swagger UI


{4} 가상환경 명령어
▶️ 가상환경 실행
source venv/bin/activate

▶️ requirements.txt 생성 및 설치
pip freeze > requirements.txt
pip install -r requirements.txt

▶️ 가상환경 해제
deactivate

▶️ Pylance 캐시 초기화
Ctrl+Shift+P → “Reload Window”



{5} Pytest 명령어(FastAPI 테스트용)
▶️ 가상환경 실행 후 가능
- 폴더 위치 backend/app 

▶️ Fixture 목록 확인
- 특정 테스트파일에서 사용 가능한 fixture들을 확인가능
- 예시: pytest --fixtures F11_tests/auth_test.py 
▶️ 예시
로그인
pytest F11_tests/auth/login_test.py -v --html=F11_tests/reports/auth/login_test.html

리프레시
pytest F11_tests/auth/refresh_test.py -v --html=F11_tests/reports/auth/refresh_test.html

로그아웃
pytest F11_tests/auth/logout_test.py -v --html=F11_tests/reports/auth/logout_test.html

미들웨어
pytest F11_tests/auth/middleware_test.py -v --html=F11_tests/reports/auth/middleware_test.html


▶️ 꿀팁: ChatGPT로 테스트 환경 빠르게 구성하기
step1: 기본 코드 준비
- conftest.py (공통 fixture)
- login_test.py (예시 테스트)
- 명령: 아래는 내 conftest.py와 login_test.py야. 이걸 기반으로 pytest 테스트 환경 만들어줘

step2: ChatGPT가 생성해준 테스트 환경 반영
step3: 에러 로그로 디버깅 



{6} Docker 명령어(개발 환경용)
- FastAPI 백엔드 실행 및 Swagger UI 확인
- docker-compose.yml이 있는 최상위 디렉토리(backend/)에서 실행해야 정상 작동
***현재 상황***
- 개발환경에서 백엔드만 가능
- 추후 개발환경 프론트도 가능하게 할 예정(그때 다시 명령어 수정)

▶️ 도커 실행 - 로그
***docker-compose.yml 폴더가 있는 곳에서 실행***
docker-compose up --build

▶️ 도커 실행 - 백그라운드
docker-compose up --build -d

▶️ 도커 실행 - 빌드없이(코드 수정 없을 경우)
docker-compose up -d

▶️ 도커 종료
***주의: 반드시 실행시킨 폴더로 가서 종료할 것***
docker-compose down


▶️ 도커 종료 - 볼륨 제거
***주의: 반드시 실행시킨 폴더로 가서 종료할 것***
docker-compose down --volumes

▶️ Swagger UI 주소 (로컬 기준)
http://localhost:{port변경}/docs

su: http://localhost:8000/docs
ha: http://localhost:8001/docs

http://localhost:5600

http://localhost:5601