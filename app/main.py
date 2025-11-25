import logging
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.api.api import api_router
from app.core.config import settings
from app.core.logging.config import setup_logging
from app.core.redis_client import redis_manager

# from sentry_sdk.integrations.logging import LoggingIntegration # (Optional, if using explicit handlers)


setup_logging()
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(">>> APPLICATION STARTUP: Initializing infrastructure... <<<")

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=1.0 if settings.ENVIRONMENT == "local" else 0.2,
            integrations=[
                FastApiIntegration(transaction_style="endpoint"),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
            send_default_pii=False,
        )
        logger.info("Checked: Sentry Integration -> ENABLED")
    else:
        logger.warning("Checked: Sentry Integration -> DISABLED (DSN not set)")

    try:
        await redis_manager.connect()
        logger.info("Checked: Redis Connection -> ESTABLISHED")
    except Exception as e:
        logger.critical(f"Startup Failed: Redis connection error: {e}")

    yield

    logger.info(">>> APPLICATION SHUTDOWN: Cleaning up resources... <<<")
    await redis_manager.close()
    logger.info("Resources released. Bye!")


app = FastAPI(
    title="FastAPI Enterprise Template",
    description="Scalable API with Sentry, Redis, and Structured Logging",
    version="1.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
)


@app.middleware("http")
async def global_exception_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.critical(
            f"Unhandled Exception ID: {request.state.request_id if hasattr(request.state, 'request_id') else 'N/A'}: {e}",
            exc_info=True,
        )

        sentry_sdk.capture_exception(e)

        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal Server Error",
                "message": "An unexpected error occurred. Our engineering team has been notified.",
            },
        )


app.include_router(api_router)


@app.get("/health", tags=["System"])
async def health_check():

    return {"status": "ok", "version": app.version}


@app.get("/sentry-debug", tags=["System"])
async def trigger_error():

    logger.error("Test error triggered manually!")
    _ = 1 / 0
