from fastapi import Request

def is_mobile_client(request: Request) -> bool:
    """User-Agent 또는 헤더를 기준으로 모바일 앱인지 판단"""
    
    client_type = request.headers.get("X-Client-Type", "").lower()
    user_agent = request.headers.get("user-agent", "").lower()
    return "mobile" in client_type or "mobile" in user_agent or "flutter" in user_agent
