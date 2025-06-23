from fastapi import Request

def extract_device_info(request: Request) -> dict:
    """요청에서 디바이스 정보를 추출합니다"""
    return {
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host,
    }