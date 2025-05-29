import random 
from app.core.config import email_redis

# Redis 저장: 키: 이메일, 값: 인증번호, 300초(5분)
async def utils_save_code(email: str, code: str):
    await email_redis.set(email, code, ex=300)

# Redis 코드 가져오기
async def utils_get_code(email: str) ->str:
    code = await email_redis.get(email)
    return code.decode() if code else None 

# 이메일과 코드 검증
async def utils_email_verify(email: str, code: str) -> bool:
    stored_code = await email_redis.get(email)
    if stored_code is None:
        return False
    return stored_code.decode() == code

# 인증 코드 생성 
async def utils_generate_verification_code()->str:
    return str(random.randint(100000, 999999))

# 코드 중복 여부 확인
async def utils_is_code_existing(email: str) -> bool:
    existing_code = await utils_get_code(email)
    return existing_code is not None