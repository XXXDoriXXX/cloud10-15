import logging
import ssl
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging.decorators import monitor_async

logger = logging.getLogger("app.redis")


class RedisManager:

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self) -> None:

        if self.client:
            return

        ssl_context = None
        if settings.REDIS_URL.startswith("rediss://"):
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

        try:

            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8",
                ssl_cert_reqs=ssl.CERT_NONE if ssl_context else None,
                max_connections=10,
                socket_timeout=5,
            )
            await self.client.ping()
            logger.info(">>> Redis connection established successfully.")

        except Exception as e:
            logger.critical(f"!!! Failed to connect to Redis: {e}", exc_info=True)
            self.client = None
            raise e

    async def close(self) -> None:
        if self.client:
            await self.client.close()
            logger.info(">>> Redis connection closed.")


redis_manager = RedisManager()


class RedisService:

    def __init__(self, client: redis.Redis):
        self.client = client

    @monitor_async(operation_name="REDIS: GET", log_args=True)
    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    @monitor_async(operation_name="REDIS: SET", log_args=True)
    async def set(self, key: str, value: str, ex: int = None) -> None:
        await self.client.set(key, value, ex=ex)

    @monitor_async(operation_name="REDIS: DELETE", log_args=True)
    async def delete(self, key: str) -> int:
        return await self.client.delete(key)

    @monitor_async(operation_name="REDIS: EXISTS", log_args=True)
    async def exists(self, key: str) -> bool:
        return await self.client.exists(key) > 0


async def get_redis_service() -> RedisService:
    if not redis_manager.client:
        raise RuntimeError("Redis client is not initialized. Check startup logs.")

    return RedisService(redis_manager.client)
