import asyncio
import asyncpg

async def test():
    conn = await asyncpg.connect(
        user="postgres",
        password="postgres",
        database="social_media_db",
        host="db",
        port=5432
    )
    print("Connected!")
    await conn.close()

asyncio.run(test())
