import tempfile
import json
import redis.asyncio as redis
from fastapi import HTTPException
from app.core.inference_client import CLIENT, MODEL_ID
from app.models.inference_dto import InferenceResultDTO
from fastapi import UploadFile


CACHE_TTL = 3600
CACHE_KEY_PREFIX = f"inference_{MODEL_ID}"


class InferenceService:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client

    async def run_inference_with_cache(self, file: UploadFile) -> dict:


        cache_key = f"{CACHE_KEY_PREFIX}_{file.filename}"

        cached_data = await self.redis_client.get(cache_key)
        if cached_data:
            print(f">>> Дані Inference для {file.filename} повернуто з Redis Cache!")
            return {"source": "cache", "data": json.loads(cached_data)}

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            content = await file.read()

            tmp.write(content)
            tmp_path = tmp.name

        print(f">>> Кешу Inference немає, запит до Roboflow для {file.filename}...")

        try:

            raw_data = CLIENT.infer(tmp_path, model_id=MODEL_ID)
            data_to_cache = json.dumps(raw_data)
            await self.redis_client.set(cache_key, data_to_cache, ex=CACHE_TTL)

            return {"source": "api", "data": raw_data}

        except Exception as e:

            raise HTTPException(status_code=500, detail=f"Roboflow API Error: {e}")

    async def run_processed_with_cache(self, file: UploadFile) -> dict:

        raw_result = await self.run_inference_with_cache(file)
        raw_data = raw_result['data']

        result = InferenceResultDTO(**raw_data)

        summary = result.summary()
        summary['source'] = raw_result['source']

        return summary