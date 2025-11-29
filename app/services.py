import asyncio
from typing import List, Dict, Optional  # <--- ADDED THIS
from fastapi import UploadFile
from .models import (
    ImageAnalysisResponse,
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
)


async def analyze_image(image: UploadFile) -> ImageAnalysisResponse:
    """
    Placeholder for a service that analyzes an image and returns a description and tags.
    """
    # Simulate a delay for a long-running process
    await asyncio.sleep(2)
    return ImageAnalysisResponse(
        description=f"A mock analysis of the image '{image.filename}'.",
        tags=["mock", "analysis", "placeholder"]
    )


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
        """
        Finds the optimal set of market candidates, allowing for "fixed" choices.
        """
        fixed_items = fixed_items or {}
        final_selections: Dict[str, MarketCandidate] = {}
        remaining_budget = max_total_budget

        # Optimization: Create a lookup for quantity to avoid looping repeatedly
        quantity_map = {item.name: item.quantity for item in detected_items}

        # --- 0. Pre-process Fixed Items ---
        items_to_optimize = []

        for item in detected_items:
            if item.name in fixed_items:
                chosen_candidate_name = fixed_items[item.name]
                # Find the chosen candidate in the map
                found = False
                for candidate in candidates_map.get(item.name, []):
                    if candidate.name == chosen_candidate_name:
                        final_selections[item.name] = candidate
                        remaining_budget -= candidate.price * quantity_map[item.name]
                        found = True
                        break
                if not found:
                    # If the fixed candidate isn't found in the map, we can't solve.
                    return None
            else:
                items_to_optimize.append(item)

        if remaining_budget < 0:
            return None  # The fixed items alone exceed the budget

        # Case: All items were fixed (no optimization needed)
        if not items_to_optimize:
            total_cost = sum(c.price * quantity_map[name] for name, c in final_selections.items())
            max_delivery = max(c.delivery_days for c in final_selections.values()) if final_selections else 0
            return Solution(selections=final_selections, total_cost=total_cost, max_delivery_days=max_delivery)

        # --- 1. Normalization for items to be optimized ---
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

        # --- 2. Recursive Solver ---
        best_solution = {"score": -1.0, "combination": None}

        def solve(item_index: int, current_combination: Dict[str, MarketCandidate]):
            # Base Case
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

            # Recursive Step
            current_item = items_to_optimize[item_index]
            for candidate in candidates_map.get(current_item.name, []):
                current_combination[current_item.name] = candidate
                solve(item_index + 1, current_combination)
                del current_combination[current_item.name]

        solve(0, {})

        # --- 3. Format Output ---
        if not best_solution["combination"]:
            # If we couldn't find a solution for the rest, return None
            return None

        # Merge optimized results with fixed items
        final_selections.update(best_solution["combination"])

        total_cost = sum(c.price * quantity_map[name] for name, c in final_selections.items())
        max_delivery_days = max(c.delivery_days for c in final_selections.values())

        return Solution(
            selections=final_selections,
            total_cost=total_cost,
            max_delivery_days=max_delivery_days,
        )

# (Keep the __main__ block if you want, or remove it since we have a dedicated validator now)