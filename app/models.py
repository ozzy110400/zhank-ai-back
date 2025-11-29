from pydantic import BaseModel
from typing import Optional


class Material(BaseModel):
    name: str
    price_per_unit: float
    units: str


class Product(BaseModel):
    name: str
    materials: list[Material]
    total_cost: Optional[float]


class ImageAnalysisResponse(BaseModel):
    """
    Represents the response from the image analysis service.
    """
    description: str
    tags: list[str]
