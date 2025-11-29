import random
import httpx
import requests
import datetime
import os
import base64
import json
from typing import List, Dict, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from .models import (
    ImageAnalysisResponse,
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
    SearchResponse,
    NegotiationResponse,
    RecalculateRequest,
)
from .services import ProcurementOptimizer, analyze_image
from .negotiation_service import NegotiationService
from dotenv import load_dotenv

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


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()
API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = 641754
CONFIG = {"vendor_name": "Custom Vendor ZHANK"}


# --- Helper for Mock Data ---
def generate_mock_candidates(items: List[DetectedItem]) -> Dict[str, List[MarketCandidate]]:
    # (Same implementation as before)
    candidates_map: Dict[str, List[MarketCandidate]] = {}
    for item in items:
        base_name = item.name.replace(" ", "")
        candidates_map[item.name] = [
            MarketCandidate(name=f"Budget {base_name}", price=round(random.uniform(80.0, 150.0), 2), delivery_days=random.randint(10, 20), quality_score=round(random.uniform(0.4, 0.6), 2), url=f"http://example.com/budget-{base_name.lower()}"),
            MarketCandidate(name=f"Standard {base_name}", price=round(random.uniform(200.0, 350.0), 2), delivery_days=random.randint(5, 9), quality_score=round(random.uniform(0.65, 0.8), 2), url=f"http://example.com/standard-{base_name.lower()}"),
            MarketCandidate(name=f"Premium {base_name} Pro", price=round(random.uniform(400.0, 600.0), 2), delivery_days=random.randint(1, 4), quality_score=round(random.uniform(0.85, 0.98), 2), url=f"http://example.com/premium-{base_name.lower()}"),
        ]
    return candidates_map


# --- API Endpoints for Human-in-the-Loop Workflow ---

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
@app.post("/openai/materials")
async def openai_materials(
    user_message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    Analyzes an image to identify materials and returns a JSON list.
    """
    system_message = {
        "role": "system",
        "content": "You are an expert in material identification. Based on the user's request and the provided image, identify the materials needed. Your response must be a JSON string list in the format: [{'name': 'Material Name', 'quantity': float}]"
    }

    messages = [system_message]

    if file:
        # Check for allowed content types
        if file.content_type not in ["image/jpeg", "image/png", "application/pdf", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a JPEG, PNG, PDF, or Excel file.")

        # Encode the image
        base64_image = base64.b64encode(await file.read()).decode('utf-8')
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_message},
                {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{base64_image}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-5.1-chat-latest",
            messages=messages
        )
        s_content = response.choices[0].message.content
        ls_content = json.loads(s_content)

        CONFIG['materials'] = ls_content
        return ls_content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/message")
def get_ai_message():
    pass


@app.post("/conversation")
def create_conversation():
    url = f"{API_BASE}/conversations/?team_id={TEAM_ID}"
    response = requests.post(url, json={
        "vendor_id": CONFIG["vendor_id"],
        "title": f"Breakdown-{datetime.datetime.now()}"
    })

    CONFIG["conversation_id"] = response.json()["id"]

    return response


@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    url = f"{API_BASE}/documents/{CONFIG['vendor_id']}/upload"
    files = {'file': (file.filename, await file.read())}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, files=files)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Error connecting to the document service: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=f"Document service returned an error: {exc.response.text}")
