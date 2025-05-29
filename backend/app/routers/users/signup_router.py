from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union

# 커스텀 모듈
from app.database.get_db import get_db
from app.schemas.user_sch import sch_user_signup
from app.services.users.signup_srv import srv_user_signup

router = APIRouter(tags=["Users"])

# 회원가입 완료 버튼 클릭 시 동작
# 전제 조건: 아이디, 닉네임, 비밀번호, 이메일 확인이 완료되어야 함
@router.post("/signup")
async def router_user_signup(request: Request, user: sch_user_signup, db: AsyncSession = Depends(get_db))->Union[bool, dict]:
    #JWT 생성 + 자동 로그인 후 메인페이지로 바로 이동
    try:
        # 프론트에서 필수 이용약관 동의 후 접근 가능, 그외 접근 시 접근 불가
        # 테스트 시에는 사용 불가
        # Referer 이용해 서버에서도 직접 호출 차단
        # referer = request.headers.get("Referer")
        # if referer is None or not referer.endswith("/terms"):
        #     raise HTTPException(status_code=403, detail="회원가입은 이용약관 동의 후에만 가능합니다.")
        
        await srv_user_signup(request, user, db)
        return {"message":"회원가입 완료되었습니다."}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
