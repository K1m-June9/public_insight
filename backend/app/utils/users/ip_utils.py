from fastapi import HTTPException, Request

def utils_ip_get(request: Request):
    client_ip = request.headers.get("X-Forwarded-For")
    if client_ip:
        # 리버스 프록시를 사용할 경우(nginx/nginx.conf)
        # X-Forwarded-For 헤더에 IP가 여러 개인 경우 첫 번째가 실제 사용자 IP
        client_ip = client_ip.split(",")[0].strip()
    else:
        # 직접 접근한 경우 FastAPI의 request.client.host 사용
        client_ip = request.client.host
    return client_ip
