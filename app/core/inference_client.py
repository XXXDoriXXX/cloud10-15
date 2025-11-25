from inference_sdk import InferenceHTTPClient

from app.core.config import settings

if not settings.ROBOFLOW_API_KEY:
    print("WARNING: ROBOFLOW_API_KEY is not set. Inference service will fail.")

CLIENT = InferenceHTTPClient(
    api_url=settings.ROBOFLOW_API_URL,
    api_key=settings.ROBOFLOW_API_KEY,
)

MODEL_ID = settings.ROBOFLOW_MODEL_ID
