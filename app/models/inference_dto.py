from typing import List

from pydantic import BaseModel, Field


class PredictionDTO(BaseModel):
    detection_id: str
    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_name: str = Field(alias="class")
    class_id: int

    @property
    def confidence_percent(self) -> float:
        return round(self.confidence * 100, 2)


class ImageInfoDTO(BaseModel):
    width: int
    height: int


class InferenceResultDTO(BaseModel):
    inference_id: str
    time: float
    image: ImageInfoDTO
    predictions: List[PredictionDTO]

    @property
    def total_objects(self) -> int:
        return len(self.predictions)

    @property
    def average_confidence(self) -> float:
        if not self.predictions:
            return 0
        return round(sum(p.confidence for p in self.predictions) / len(self.predictions) * 100, 2)

    def summary(self) -> dict:
        return {
            "total_people": self.total_objects,
            "avg_confidence_%": self.average_confidence,
            "detailed_confidences": [
                {"id": p.detection_id, "confidence_%": p.confidence_percent} for p in self.predictions
            ],
            "image_resolution": f"{self.image.width}x{self.image.height}",
            "inference_time_sec": round(self.time, 3),
        }
