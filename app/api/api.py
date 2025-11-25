from fastapi import APIRouter

from app.api.endpoints import cache, users

api_router = APIRouter()
api_router.include_router(users.router)
api_router.include_router(cache.router)
