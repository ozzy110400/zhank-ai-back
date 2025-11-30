import base64
import json
import urllib.parse
from typing import List, Dict, Optional

from fastapi import UploadFile, HTTPException
from openai import OpenAI
from dotenv import load_dotenv

from .models import (
    ImageAnalysisResponse,
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
)

# Load env to get OPENAI_API_KEY
load_dotenv()

# Initialize OpenAI Client
client = OpenAI()

# --- Simple In-Memory Cache for Images ---
IMAGE_CACHE = {}


async def analyze_image(image: UploadFile, user_message: Optional[str] = None) -> ImageAnalysisResponse:
    """
    Analyzes an uploaded image using OpenAI GPT-4o to identify office items.
    """
    if image.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image type. Please upload JPEG, PNG, or WebP."
        )

    file_content = await image.read()
    base64_image = base64.b64encode(file_content).decode('utf-8')

    system_prompt = (
        "You are an expert procurement assistant. Analyze the image and identify the furniture or office equipment present. "
        "Return a JSON object with a single key 'items' containing a list of items. "
        "Each item must have: "
        "'name' (string, generic name like 'Office Chair'), "
        "'quantity' (integer), "
        "and 'target_material' (string, inferred material like 'Mesh', 'Wood', 'Plastic' or null). "
        "Also provide a short 'description' of the scene and a list of 'tags'."
    )

    text_prompt = "What items do we need to buy based on this image?"
    if user_message:
        text_prompt = f"What items do we need to buy? User notes: {user_message}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image.content_type};base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content
        data = json.loads(content)

        items_data = data.get("items", [])
        description = data.get("description", "Image analysis complete.")
        tags = data.get("tags", [])

        detected_items = [
            DetectedItem(
                name=item["name"],
                quantity=item["quantity"] if "quantity" in item and item["quantity"] else 1,
                target_material=item.get("target_material")
            )
            for item in items_data
        ]

        return ImageAnalysisResponse(
            description=description,
            tags=tags,
            detected_items=detected_items
        )

    except Exception as e:
        print(f"OpenAI Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


def find_product_image(product_name: str) -> str:
    """
    Generates a realistic AI image of the product using Pollinations.ai.
    This replaces search engines entirely to ensure 100% uptime and no broken links.
    """
    # 1. Check Cache
    if product_name in IMAGE_CACHE:
        return IMAGE_CACHE[product_name]

    print(f"Generating AI image for: {product_name}...")

    # 2. Construct Prompt for Pollinations
    # We add keywords like "product shot", "white background", "high quality" to make it look like e-commerce.
    encoded_name = urllib.parse.quote(product_name)
    image_url = f"https://image.pollinations.ai/prompt/professional_product_photography_of_{encoded_name}_modern_furniture_white_studio_background_8k?nologo=true"

    # 3. Cache and Return
    IMAGE_CACHE[product_name] = image_url
    return image_url


class ProcurementOptimizer:
    """
    Handles the logic for finding the best procurement options based on user preferences.
    """

    def find_constrained_optimal_setup(
            self,
            detected_items: List[DetectedItem],
            candidates_map: Dict[str, List[MarketCandidate]],
            preferences: UserPreferences,
            max_total_budget: float,
            fixed_items: Optional[Dict[str, str]] = None
    ) -> Optional[Solution]:

        fixed_items = fixed_items or {}
        final_selections: Dict[str, MarketCandidate] = {}
        remaining_budget = max_total_budget

        quantity_map = {item.name: item.quantity for item in detected_items}
        items_to_optimize = []

        for item in detected_items:
            if item.name in fixed_items:
                chosen_candidate_name = fixed_items[item.name]
                found = False
                for candidate in candidates_map.get(item.name, []):
                    if candidate.name == chosen_candidate_name:
                        final_selections[item.name] = candidate
                        remaining_budget -= candidate.price * quantity_map[item.name]
                        found = True
                        break
                if not found:
                    return None
            else:
                items_to_optimize.append(item)

        if remaining_budget < 0:
            return None

        if not items_to_optimize:
            total_cost = sum(c.price * quantity_map[name] for name, c in final_selections.items())
            max_delivery = max(c.delivery_days for c in final_selections.values()) if final_selections else 0
            return Solution(selections=final_selections, total_cost=total_cost, max_delivery_days=max_delivery)

        normalized_scores: Dict[str, Dict[str, float]] = {}
        for item in items_to_optimize:
            candidates = candidates_map.get(item.name, [])
            if not candidates:
                continue

            normalized_scores[item.name] = {}
            prices = [c.price for c in candidates]
            delivery_days = [c.delivery_days for c in candidates]
            quality_scores = [c.quality_score for c in candidates]

            min_price, max_price = min(prices), max(prices)
            min_days, max_days = min(delivery_days), max(delivery_days)
            min_quality, max_quality = min(quality_scores), max(quality_scores)
            epsilon = 1e-9

            for c in candidates:
                norm_price = 1 - ((c.price - min_price) / (max_price - min_price + epsilon))
                norm_delivery = 1 - ((c.delivery_days - min_days) / (max_days - min_days + epsilon))
                norm_quality = (c.quality_score - min_quality) / (max_quality - min_quality + epsilon)

                final_score = (
                        (norm_price * preferences.price_weight) +
                        (norm_delivery * preferences.delivery_weight) +
                        (norm_quality * preferences.quality_weight)
                )
                normalized_scores[item.name][c.name] = final_score

        best_solution = {"score": -1.0, "combination": None}

        def solve(item_index: int, current_combination: Dict[str, MarketCandidate]):
            if item_index == len(items_to_optimize):
                current_cost = sum(
                    c.price * quantity_map[name]
                    for name, c in current_combination.items()
                )

                if current_cost > remaining_budget:
                    return

                total_score = sum(normalized_scores[name][c.name] for name, c in current_combination.items())

                if total_score > best_solution["score"]:
                    best_solution["score"] = total_score
                    best_solution["combination"] = current_combination.copy()
                return

            current_item = items_to_optimize[item_index]
            for candidate in candidates_map.get(current_item.name, []):
                current_combination[current_item.name] = candidate
                solve(item_index + 1, current_combination)
                del current_combination[current_item.name]

        solve(0, {})

        if not best_solution["combination"]:
            return None

        final_selections.update(best_solution["combination"])

        total_cost = sum(c.price * quantity_map[name] for name, c in final_selections.items())
        max_delivery_days = max(c.delivery_days for c in final_selections.values())

        return Solution(
            selections=final_selections,
            total_cost=total_cost,
            max_delivery_days=max_delivery_days,
        )