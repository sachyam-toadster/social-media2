# src/db/redis.py
from redis.asyncio import Redis
from src.config import settings as Config

JTI_EXPIRY = 3600

token_blocklist = Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    val = await token_blocklist.get(jti)
    return val is not None
