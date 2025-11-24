import redis.asyncio as redis
from app.core.config import settings
import ssl
redis_client: redis.Redis | None = None


async def init_redis():

    global redis_client

    ssl_required = settings.REDIS_URL.startswith("rediss://")

    ssl_context = ssl.create_default_context() if ssl_required else None

    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            ssl_cert_reqs=ssl_context.verify_mode if ssl_context else None,
            ssl_certfile=None,
        )

        await redis_client.ping()
        print(">>> Redis connection established successfully.")

    except Exception as e:
        redis_client = None
        print(f"!!! Failed to connect to Redis: {e}")


async def close_redis():
    if redis_client:
        await redis_client.close()
        print(">>> Redis connection closed.")