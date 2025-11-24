from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.core import redis_client
import redis.asyncio as redis
from app.services.inference_service import InferenceService
from fastapi.responses import JSONResponse

def get_current_redis_client() -> redis.Redis:
    if not redis_client.redis_client:
        msg = "Redis client not initialized."
        print(msg)
        raise HTTPException(status_code=500, detail=msg)
    return redis_client.redis_client

def get_inference_service(r: redis.Redis = Depends(get_current_redis_client)) -> InferenceService:
    return InferenceService(redis_client=r)

router = APIRouter(tags=["Cache & Inference API"])


@router.post("/cache/set", status_code=status.HTTP_200_OK, summary="Встановити значення у Redis за ключем")
async def set_cache_value(
    key: str,
    value: str,
    r: redis.Redis = Depends(get_current_redis_client)
):
    await r.set(key, value)
    return {"message": f"Key '{key}' set successfully"}


@router.get("/cache/get/{key}", summary="Отримати значення з Redis за ключем")
async def get_cache_value(
    key: str,
    r: redis.Redis = Depends(get_current_redis_client)
):
    value = await r.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found in cache")
    return {"key": key, "value": value}



@router.post("/infer/raw", summary="Виконати Inference (Roboflow) та кешувати сирий результат")
async def infer_raw(
    file: UploadFile = File(...),
    service: InferenceService = Depends(get_inference_service)
):
    data = await service.run_inference_with_cache(file)
    return JSONResponse(content=data)


@router.post("/infer/summary", summary="Виконати Inference, кешувати та повернути зведення")
async def infer_processed(
    file: UploadFile = File(...),
    service: InferenceService = Depends(get_inference_service)
):
    summary = await service.run_processed_with_cache(file)
    return JSONResponse(content=summary)