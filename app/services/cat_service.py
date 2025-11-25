import json

import httpx
import redis.asyncio as redis
from fastapi import HTTPException

CAT_API_URL = "https://api.thecatapi.com/v1/images/search"
CACHE_TTL = 60


class CatAPIService:

    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def get_cached_cat_image(self):
        cache_key = "cached_cat_data"

        cached_data = await self.redis_client.get(cache_key)

        if cached_data:
            print(">>> Дані повернуто з Redis Cache!")

            return {"source": "cache", "data": json.loads(cached_data)}

        print(">>> Кешу немає, запит до зовнішнього API...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(CAT_API_URL)
                response.raise_for_status()

                api_data = response.json()[0]
                data_to_cache = json.dumps(api_data)
                await self.redis_client.set(cache_key, data_to_cache, ex=CACHE_TTL)

                return {"source": "api", "data": api_data}

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"External API Error: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
