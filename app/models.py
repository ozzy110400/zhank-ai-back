from pydantic import BaseModel, Field, model_validator
from typing import Dict, Optional, List
from math import isclose


class ImageAnalysisResponse(BaseModel):
    """
    Represents the response from the image analysis service.
    """
    description: str
    tags: list[str]


class DetectedItem(BaseModel):
    name: str
    quantity: int
    target_material: Optional[str] = None


class MarketCandidate(BaseModel):
    name: str
    price: float
    delivery_days: int
    quality_score: float  # Assuming a score from 0.0 to 1.0
    url: str
    is_selected: bool = False


class UserPreferences(BaseModel):
    price_weight: float = Field(..., ge=0.0, le=1.0)
    delivery_weight: float = Field(..., ge=0.0, le=1.0)
    quality_weight: float = Field(..., ge=0.0, le=1.0)

    @model_validator(mode='after')
    def check_weights_sum(self) -> 'UserPreferences':
        # Ensure weights sum to 1 for clear, interpretable scoring
        total = self.price_weight + self.delivery_weight + self.quality_weight
        if not isclose(total, 1.0):
            raise ValueError("The sum of price, delivery, and quality weights must be 1.0")
        return self


class Solution(BaseModel):
    selections: Dict[str, MarketCandidate]
    total_cost: float
    max_delivery_days: int


class FinalReport(BaseModel):
    original_solution: Solution
    negotiated_solution: Solution
    savings_amount: float
    savings_percentage: float
    processing_logs: List[str]


# --- New Models for Human-in-the-Loop Workflow ---

class NegotiationResponse(BaseModel):
    text_response: str
    audio_base64: str
    conversation_id: int
    parsed_new_price: Optional[float] = None


class RecalculateRequest(BaseModel):
    detected_items: List[DetectedItem]
    candidates_map: Dict[str, List[MarketCandidate]]
    preferences: UserPreferences
    budget: float
    fixed_items: Dict[str, str]  # Maps item name (e.g., "Office Chair") to a fixed candidate name


class SearchResponse(BaseModel):
    all_candidates: Dict[str, List[MarketCandidate]]
    initial_solution: Optional[Solution]
    logs: List[str]
