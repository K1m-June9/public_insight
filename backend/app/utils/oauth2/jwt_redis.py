from app.core.config import login_redis, settings

# Access Token 블랙리스트 등록 utils_access_token_blacklist(username, device_id, jti 기반)
async def utils_access_token_blacklist(username:str, device_id:str, jti: str = None):
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    key = f"blacklist:{username}:{device_id}:{jti}"
    await login_redis.setex(key, expire_seconds, "true")


# Access Token 블랙리스트 확인 (username + device_id + jti  기반)
async def utils_is_access_token_blacklisted(username:str, device_id:str, jti:str) -> bool:
    key = f"blacklist:{username}:{device_id}:{jti}"
    return await login_redis.get(key) is not None


# Refresh Token 사용된 토큰 기록
async def utils_mark_refresh_token_used(refresh_token:str, ttl: int = 3600):
    await login_redis.setex(f"used_refresh_token:{refresh_token}", ttl, "true")


# Refresh Token 재사용 여부 확인(재사용 방지)
async def utils_is_refresh_token_used(refresh_token:str)->bool:
    return bool(await login_redis.exists(f"used_refresh_token:{refresh_token}"))