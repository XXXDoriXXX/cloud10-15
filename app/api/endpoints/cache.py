from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.core.redis_client import RedisService, get_redis_service
from app.services.inference_service import InferenceService

router = APIRouter(tags=["Cache & Inference API"])


def get_inference_service(redis_service: RedisService = Depends(get_redis_service)) -> InferenceService:
    return InferenceService(redis_service=redis_service)


@router.post("/cache/set", status_code=status.HTTP_200_OK, summary="Встановити значення у Redis (Monitor enabled)")
async def set_cache_value(key: str, value: str, redis_service: RedisService = Depends(get_redis_service)):

    await redis_service.set(key, value)
    return {"message": f"Key '{key}' set successfully"}


@router.get("/cache/get/{key}", summary="Отримати значення з Redis (Monitor enabled)")
async def get_cache_value(key: str, redis_service: RedisService = Depends(get_redis_service)):

    value = await redis_service.get(key)

    if value is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Key '{key}' not found in cache")

    return {"key": key, "value": value}


@router.post("/infer/raw", summary="Виконати Inference (Roboflow) та кешувати сирий результат")
async def infer_raw(file: UploadFile = File(...), service: InferenceService = Depends(get_inference_service)):

    data = await service.run_inference_with_cache(file)
    return JSONResponse(content=data)


@router.post("/infer/summary", summary="Виконати Inference, кешувати та повернути зведення")
async def infer_processed(file: UploadFile = File(...), service: InferenceService = Depends(get_inference_service)):

    summary = await service.run_processed_with_cache(file)
    return JSONResponse(content=summary)
