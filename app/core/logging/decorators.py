import functools
import logging
import time
from typing import Any, Callable

import sentry_sdk

logger = logging.getLogger("app.performance")


def monitor_async(operation_name: str, log_args: bool = False):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            extra_info = f"args={args} kwargs={kwargs}" if log_args else ""

            logger.info(f"[START] {operation_name} {extra_info}")
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                execution_time = time.time() - start_time
                logger.info(f"[SUCCESS] {operation_name} - Duration: {execution_time:.4f}s")

                return result

            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f"[ERROR] {operation_name} failed after {execution_time:.4f}s: {str(e)}")

                with sentry_sdk.push_scope() as scope:
                    scope.set_tag("operation", operation_name)
                    scope.set_extra("execution_time", execution_time)
                    sentry_sdk.capture_exception(e)

                raise e

        return wrapper

    return decorator
