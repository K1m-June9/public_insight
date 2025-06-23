from app.F5_core.redis import token_redis
from app.F7_models.users import User
from datetime import timedelta

class RedisCacheService:
    @staticmethod
    async def cache_user_info(user: User):
        """유저 정보를 Redis에 캐싱 (1일 후 만료)"""
        user_data = {
            "user_id": user.user_id,
            "role": user.role.value,
            "status": user.status.value
        }
        await token_redis.hmset(f"user:{user.user_id}", user_data)
        await token_redis.expire(f"user:{user.user_id}", timedelta(days=1))
    
    @staticmethod
    async def get_cached_user_info(user_id: str):
        """Redis에서 유저 정보 조회"""
        return await token_redis.hgetall(f"user:{user_id}")
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """유저 캐시 무효화 (삭제)"""
        await token_redis.delete(f"user:{user_id}")