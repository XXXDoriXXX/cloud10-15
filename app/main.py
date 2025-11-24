from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.api import api_router
from app.core.redis_client import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup: Initializing Redis...")
    await init_redis()
    yield
    print("Application shutdown: Closing Redis connection...")
    await close_redis()

app = FastAPI(
    title="FastAPI PostgreSQL & Redis Cache",
    description="Реалізація CRUD",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI service. Check /docs for endpoints."}