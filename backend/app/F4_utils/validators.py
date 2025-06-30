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
    - 길이: 한글 기준 2글자 이상 12글자 이하
    - 이모지 금지
    - 특수문자 금지 (유니코드 범위 내 특수기호)
    - 금지 단어 포함 불가 (운영자, admin, 중재자, moderator)
    """
    # 1) 공백 검사
    if " " in nickname:
        return False

    # 2) 금지 단어 검사 (소문자 변환 후 검사)
    forbidden_words = ["운영자", "admin", "중재자", "moderator"]
    lowered = nickname.lower()
    if any(word in lowered for word in forbidden_words):
        return False

    # 3) 이모지 및 특수문자 검사
    # 이모지 범위: 유니코드에서 이모지는 여러 블록에 분산되어 있어,
    # 아래 패턴으로 대략 검사함
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
        "\U0001F680-\U0001F6FF"  # Transport & Map Symbols
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    if emoji_pattern.search(nickname):
        return False

    # 4) 허용 문자 검사: 한글, 영어, 숫자만 허용
    # 유니코드 한글 영역: 가(0xAC00) ~ 힣(0xD7A3)
    for char in nickname:
        code = ord(char)
        if char.isdigit():
            continue
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            continue
        if 0xAC00 <= code <= 0xD7A3:
            continue
        # 위 외 문자 있으면 불가
        return False

    # 5) 길이 체크 (한글 기준 2~12자)
    # 한글 1자 == 2 bytes가 아니라, 여기선 "글자수" 기준임.
    length = 0
    for ch in nickname:
        # 한글 1글자 = 1, 영문/숫자도 1로 카운트
        length += 1
    if length < 2 or length > 12:
        return False

    return True