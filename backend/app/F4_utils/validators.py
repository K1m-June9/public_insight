import re
import unicodedata
import logging

from fastapi import HTTPException, status


logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(
    r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
)

def validate_user_id(user_id: str):
    """user_id 유효성 검사"""

    # 1. 공백 포함 금지
    if " " in user_id:
        logger.warning(f"[user_id] 공백 포함 - {user_id}")
        return False

    # 2. 길이: 8~20자
    if not (8 <= len(user_id) <= 20):
        logger.warning(f"[user_id] 길이 제한 위반 (8~20자) - {user_id}")
        return False

    # 3. 영문 소문자와 숫자만 허용
    if not re.fullmatch(r"[a-z0-9]+", user_id):
        logger.warning(f"[user_id] 영문 소문자/숫자 외 문자 포함 - {user_id}")
        return False

    # 4. 숫자로 시작 금지
    if user_id[0].isdigit():
        logger.warning(f"[user_id] 숫자로 시작 - {user_id}")
        return False

    return True


def validate_password(password: str):
    """password 유효성 검사"""
    # 1. 공백 금지
    if " " in password:
        logger.warning("[password] 공백 포함")
        return False
    
    # 2. 길이: 10~25자
    if not (10 <= len(password) <= 25):
        logger.warning(f"[password] 길이 제한 위반 (8~25자) - {password}")
        return False

    # 3. 허용 문자 제한: 영문 소문자, 숫자, 특수문자 (!@$%^&*+~)
    if not re.fullmatch(r"[a-z0-9!@$%^&*+~]+", password):
        logger.warning("[password] 허용되지 않은 문자 포함")
        return False

    # 4. 필수 문자 포함: 소문자, 숫자, 특수문자
    if not re.search(r"[a-z]", password):
        logger.warning("[password] 소문자 없음")
        return False

    if not re.search(r"[0-9]", password):
        logger.warning("[password] 숫자 없음")
        return False

    if not re.search(r"[!@$%^&*+~]", password):
        logger.warning("[password] 특수문자 없음")
        return False

    # 5. 첫 글자가 특수문자이면 안 됨
    if re.match(r"[!@$%^&*+~]", password[0]):
        logger.warning("[password] 첫 글자가 특수문자")
        return False

    return True

def validate_email(email: str) -> bool:
    """이메일 형식이 유효한지 검사"""
    if not email:
        return False
    return bool(EMAIL_REGEX.match(email))



def validate_nickname(nickname: str) -> bool:
    """
    닉네임 유효성 검사
    
    규칙:
    - 공백 불가
    - 허용 문자: 한글, 영어(대소문자), 숫자
    - 길이: 2~12자
    - 이모지 및 기타 특수문자 금지
    - 금지 단어 포함 불가
    """
    # 1. 길이 검사
    if not (2 <= len(nickname) <= 12):
        return False 
    
    # 2. 공백 검사
    if " " in nickname:
        return False 
    
    # 3. 허용 문자 검사(한글, 영문, 숫자 외 모든 문자 필터링)
    if not re.fullmatch(r"^[a-zA-Z0-9가-힣]+$", nickname):
        return False
    
    # 4. 금지 단어 검사
    forbidden_words = ["운영자", "admin", "중재자", "moderator"]
    if any(word in nickname.lower() for word in forbidden_words):
        return False


    return True