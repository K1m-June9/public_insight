import re
from sqlalchemy.ext.asyncio import AsyncSession

#커스텀 모듈
from app.repositories.check.ban_check_repo import repo_id_banned_keywords

# User ID 규칙 체크
def utils_id_rule(username:str) -> bool:
    # 공백 금지
    if " " in username:
        return False
    
    # 아이디 길이 검사(8글자~12글자)
    if not (8 <= len(username) <= 12 ):
        return False
    
    # 영문 소문자(a-z), 숫자(0-9)
    pattern = r"^[a-z0-9]+$"
    if not re.fullmatch(pattern, username):
        return False
    
    # 시작이 숫자로 시작하는 경우 금지
    if re.match(r"^\d", username):
        return False

    # 연속 숫자 또는 연속 문자 사용 금지(예: 111, aaa)
    if re.search(r"(.)\1{2,}", username):
        return False
    
    return True

# User ID 금칙어 체크
async def utils_id_banned_keywords(db:AsyncSession, username:str)->bool:
    #영어 부분만 추출
    username_parts = re.findall(r'[a-zA-Z]+', username)
    if username_parts:
        return await repo_id_banned_keywords(db, username_parts)
    return True

# Nickname 규칙 체크
def utils_nickname_rule(nickname:str) -> bool:
    # 공백 금지
    if " " in nickname:
        return False
    
    # 길이 검사(2글자~8글자)
    if not (2 <= len(nickname) <= 8):
        return False
    
    # 영어, 숫자, 한글만 허용
    if re.search(r"[^a-zA-Z0-9가-힣]", nickname):
        return False
    return True


# password 규칙 체크
def utils_password_rule(password:str)->bool:
    # 공백 금지
    if " " in password:
        return False
    
    # 아이디 길이 검사(8글자~32글자)
    if not (8 <= len(password) <= 32 ):
        return False
    
    # 영문 소문자, 숫자, 지정 특수문자 외 사용 금지
    if not re.fullmatch(r"[a-z0-9!@$%^&*+~]+", password):
        return False
    
    # 영문 소문자, 숫자, 특수문자 조합 확인
    if not (re.search(r"[a-z]", password) and re.search(r"\d", password) and re.search(r"[!@$%^&*+~]", password)):
        return False
    
    # 맨 앞에 특수문자 금지
    if re.match(r"^[!@$%^&*+~]", password):
        return False
    
    return True

