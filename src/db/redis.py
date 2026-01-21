# src/db/redis.py
from redis.asyncio import Redis
from src.config import settings as Config

JTI_EXPIRY = 3600

redis = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)

async def add_jti_to_blocklist(jti: str) -> None:
    await redis.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    val = await redis.get(jti)
    return val is not None

REFRESH_TOKEN_EXPIRY = 7 * 24 * 60 * 60  # 7 days

async def store_refresh_token(user_id: str, refresh_token: str) -> None:
    await redis.set(
        name=f"refresh:{user_id}",
        value=refresh_token,
        ex=REFRESH_TOKEN_EXPIRY
    )

async def get_refresh_token(user_id: str) -> str | None:
    return await redis.get(f"refresh:{user_id}")

async def delete_refresh_token(user_id: str) -> None:
    await redis.delete(f"refresh:{user_id}")