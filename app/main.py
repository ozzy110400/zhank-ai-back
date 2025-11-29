import random
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import (
    ImageAnalysisResponse,
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    FinalReport,
)
from .services import analyze_image
from .negotiation_service import ProcurementOrchestrator

app = FastAPI(
    title="Office Procurement AI",
    description="An API for automating office procurement using computer vision and optimization.",
    version="1.0.0",
)

# Add CORS middleware to allow all origins for the Hackathon demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# 1. Request Model
class ProcurementRequest(BaseModel):
    detected_items: List[DetectedItem]
    preferences: UserPreferences
    budget: float


# 2. Mock Scraper
def generate_mock_candidates(items: List[DetectedItem]) -> Dict[str, List[MarketCandidate]]:
    """
    Generates a mock list of market candidates for each detected item.
    In a real application, this would be the output of a web scraping service.
    """
    candidates_map: Dict[str, List[MarketCandidate]] = {}
    for item in items:
        base_name = item.name.replace(" ", "")
        candidates_map[item.name] = [
            # Option A: Low price, Slow delivery, Low quality
            MarketCandidate(
                name=f"Budget {base_name}",
                price=round(random.uniform(80.0, 150.0), 2),
                delivery_days=random.randint(10, 20),
                quality_score=round(random.uniform(0.4, 0.6), 2),
                url=f"http://example.com/budget-{base_name.lower()}",
            ),
            # Option B: Medium price, Medium delivery, Medium quality
            MarketCandidate(
                name=f"Standard {base_name}",
                price=round(random.uniform(200.0, 350.0), 2),
                delivery_days=random.randint(5, 9),
                quality_score=round(random.uniform(0.65, 0.8), 2),
                url=f"http://example.com/standard-{base_name.lower()}",
            ),
            # Option C: High price, Fast delivery, High quality
            MarketCandidate(
                name=f"Premium {base_name} Pro",
                price=round(random.uniform(400.0, 600.0), 2),
                delivery_days=random.randint(1, 4),
                quality_score=round(random.uniform(0.85, 0.98), 2),
                url=f"http://example.com/premium-{base_name.lower()}",
            ),
        ]
    return candidates_map


# 3. API Endpoints
@app.post("/procure/optimize", response_model=FinalReport)
async def optimize_procurement(request: ProcurementRequest):
    """
    Runs the full procurement orchestration:
    - Generates mock market data based on detected items.
    - Finds an initial optimal solution based on budget and preferences.
    - Simulates negotiating prices for high-value items.
    - Re-optimizes to find the final, best-value solution.
    """
    # Step 1: Simulate finding products online
    market_candidates = generate_mock_candidates(request.detected_items)

    # Step 2: Initialize and run the full orchestration process
    orchestrator = ProcurementOrchestrator()
    final_report = orchestrator.run_full_process(
        detected_items=request.detected_items,
        candidates_map=market_candidates,
        preferences=request.preferences,
        max_total_budget=request.budget,
    )

    # Step 3: Handle cases where no solution is possible
    if not final_report:
        raise HTTPException(
            status_code=404,
            detail="Could not find any procurement solution that fits the given budget and preferences."
        )

    return final_report


@app.post("/upload-image/", response_model=ImageAnalysisResponse)
async def upload_image(image: UploadFile = File(...)):
    """
    Accepts an image file, passes it to a service for analysis,
    and returns the analysis result. (Mocked)
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type. Please upload an image.")

    # The service function simulates a long-running CV analysis
    analysis_result = await analyze_image(image)
    return analysis_result
