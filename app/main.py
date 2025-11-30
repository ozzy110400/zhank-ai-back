import random
from typing import List, Dict, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from .models import (
    ImageAnalysisResponse,
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    SearchResponse,
    NegotiationResponse,
    RecalculateRequest,
)
from .services import ProcurementOptimizer, analyze_image, find_product_image  # <--- Imported find_product_image
from .negotiation_service import NegotiationService

# Load env variables (OPENAI_API_KEY)
load_dotenv()

app = FastAPI(
    title="Office Procurement AI (Co-Pilot)",
    description="An API for a human-in-the-loop procurement process.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request Models for new endpoints ---
class SearchRequest(BaseModel):
    detected_items: List[DetectedItem]
    preferences: UserPreferences
    budget: float


class NegotiationStartRequest(BaseModel):
    candidate_name: str


class NegotiationMessageRequest(BaseModel):
    conversation_id: int
    message_content: str


# --- Helper for Mock Data ---
def generate_mock_candidates(items: List[DetectedItem]) -> Dict[str, List[MarketCandidate]]:
    # Mock Scraper logic
    candidates_map: Dict[str, List[MarketCandidate]] = {}
    for item in items:
        base_name = item.name.replace(" ", "")
        candidates_map[item.name] = [
            MarketCandidate(
                name=f"Budget {base_name}",
                price=round(random.uniform(80.0, 150.0), 2),
                delivery_days=random.randint(10, 20),
                quality_score=round(random.uniform(0.4, 0.6), 2),
                url=f"http://example.com/budget-{base_name.lower()}",
            ),
            MarketCandidate(
                name=f"Standard {base_name}",
                price=round(random.uniform(200.0, 350.0), 2),
                delivery_days=random.randint(5, 9),
                quality_score=round(random.uniform(0.65, 0.8), 2),
                url=f"http://example.com/standard-{base_name.lower()}",
            ),
            MarketCandidate(
                name=f"Premium {base_name} Pro",
                price=round(random.uniform(400.0, 600.0), 2),
                delivery_days=random.randint(1, 4),
                quality_score=round(random.uniform(0.85, 0.98), 2),
                url=f"http://example.com/premium-{base_name.lower()}",
            ),
        ]
    return candidates_map


# --- API Endpoints ---

@app.get("/product/image")
async def get_product_image(name: str):
    """
    Finds an image URL for a given product name using DuckDuckGo Search.
    Uses in-memory caching to prevent rate limits.
    """
    image_url = find_product_image(name)
    return {"image_url": image_url}


@app.post("/upload-image/", response_model=ImageAnalysisResponse)
async def upload_image(image: UploadFile = File(...), message: Optional[str] = Form(None)):
    """
    Accepts an image file, sends it to OpenAI GPT-4o for analysis,
    and returns a structured list of detected items (name, quantity, material).
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type. Please upload an image.")

    # Call the real OpenAI service
    analysis_result = await analyze_image(image, user_message=message)
    return analysis_result


@app.post("/procure/search", response_model=SearchResponse)
async def search_procurement_options(request: SearchRequest):
    """
    Step 1: Generates candidates, finds an initial optimal solution,
    and returns ALL candidates with the winners flagged.
    """
    logs = ["Starting procurement search..."]

    # 1. Generate mock candidates
    market_candidates = generate_mock_candidates(request.detected_items)
    logs.append(f"Generated {sum(len(v) for v in market_candidates.values())} market candidates for {len(request.detected_items)} item types.")

    # 2. Run the optimizer to find the initial best setup
    optimizer = ProcurementOptimizer()
    initial_solution = optimizer.find_constrained_optimal_setup(
        detected_items=request.detected_items,
        candidates_map=market_candidates,
        preferences=request.preferences,
        max_total_budget=request.budget,
    )
    logs.append("Initial optimization complete.")

    # 3. Flag the selected candidates
    if initial_solution:
        logs.append(f"Initial solution found with total cost: ${initial_solution.total_cost:.2f}")
        for item_name, selected_candidate in initial_solution.selections.items():
            for candidate in market_candidates.get(item_name, []):
                if candidate.name == selected_candidate.name:
                    candidate.is_selected = True
                    break
    else:
        logs.append("No solution found within the given budget.")

    return SearchResponse(
        all_candidates=market_candidates,
        initial_solution=initial_solution,
        logs=logs,
    )


@app.post("/negotiate/start", response_model=Dict[str, int])
async def start_negotiation(request: NegotiationStartRequest):
    """
    Step 2a: Starts a negotiation conversation for a specific candidate.
    """
    negotiator = NegotiationService()
    conversation_id = negotiator.start_conversation(request.candidate_name)
    if not conversation_id:
        raise HTTPException(status_code=500, detail="Failed to start conversation with vendor API.")
    return {"conversation_id": conversation_id}


@app.post("/negotiate/message", response_model=NegotiationResponse)
async def message_negotiation(request: NegotiationMessageRequest):
    """
    Step 2b: Sends a message in a negotiation and gets the vendor's audio/text reply.
    """
    negotiator = NegotiationService()
    response = negotiator.send_message(request.conversation_id, request.message_content)
    if not response:
        raise HTTPException(status_code=500, detail="Failed to get response from vendor API.")

    text_reply, audio_base64, parsed_price = response
    return NegotiationResponse(
        text_response=text_reply,
        audio_base64=audio_base64,
        conversation_id=request.conversation_id,
        parsed_new_price=parsed_price,
    )


@app.post("/procure/recalculate", response_model=SearchResponse)
async def recalculate_procurement(request: RecalculateRequest):
    """
    Step 3: Re-runs the optimizer with updated prices and fixed items.
    """
    logs = ["Re-calculating optimal solution with new constraints..."]

    optimizer = ProcurementOptimizer()
    new_solution = optimizer.find_constrained_optimal_setup(
        detected_items=request.detected_items,
        candidates_map=request.candidates_map,
        preferences=request.preferences,
        max_total_budget=request.budget,
        fixed_items=request.fixed_items,
    )
    logs.append("Re-optimization complete.")

    # Flag the new selections
    if new_solution:
        logs.append(f"New solution found with total cost: ${new_solution.total_cost:.2f}")
        # First, reset all `is_selected` flags
        for category in request.candidates_map.values():
            for cand in category:
                cand.is_selected = False
        # Then, set the new ones
        for item_name, selected_candidate in new_solution.selections.items():
            for candidate in request.candidates_map.get(item_name, []):
                if candidate.name == selected_candidate.name:
                    candidate.is_selected = True
                    break
    else:
        logs.append("No new solution could be found with the updated constraints.")

    return SearchResponse(
        all_candidates=request.candidates_map,
        initial_solution=new_solution,
        logs=logs,
    )