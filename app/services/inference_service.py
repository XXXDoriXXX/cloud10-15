import json
import os
import tempfile
from typing import Any, Dict

from fastapi import HTTPException, UploadFile, status

from app.core.inference_client import CLIENT, MODEL_ID
from app.core.logging.decorators import monitor_async
from app.core.redis_client import RedisService
from app.models.inference_dto import InferenceResultDTO

CACHE_TTL = 3600
CACHE_KEY_PREFIX = f"inference:{MODEL_ID}"


class InferenceService:
    def __init__(self, redis_service: RedisService):
        self.redis = redis_service

    @monitor_async(operation_name="EXTERNAL_API: Roboflow Inference", log_args=False)
    async def _execute_external_inference(self, image_path: str) -> Dict[str, Any]:

        return CLIENT.infer(image_path, model_id=MODEL_ID)

    @monitor_async(operation_name="SERVICE: Inference Pipeline", log_args=False)
    async def run_inference_with_cache(self, file: UploadFile) -> Dict[str, Any]:

        cache_key = f"{CACHE_KEY_PREFIX}:{file.filename}"

        cached_data = await self.redis.get(cache_key)
        if cached_data:

            return {"source": "cache", "data": json.loads(cached_data)}

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name

            raw_data = await self._execute_external_inference(tmp_path)

            await self.redis.set(key=cache_key, value=json.dumps(raw_data), ex=CACHE_TTL)

            return {"source": "api", "data": raw_data}

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Inference provider failed: {str(e)}"
            )

        finally:

            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    @monitor_async(operation_name="SERVICE: Process Result", log_args=False)
    async def run_processed_with_cache(self, file: UploadFile) -> Dict[str, Any]:
        try:
            raw_result = await self.run_inference_with_cache(file)
            raw_data = raw_result["data"]

            result_dto = InferenceResultDTO(**raw_data)

            summary = result_dto.summary()
            summary["source"] = raw_result["source"]

            return summary

        except KeyError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Invalid response format from ML model")
        except Exception as e:
            raise e
