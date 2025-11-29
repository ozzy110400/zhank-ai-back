import asyncio
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
    In a real application, this would involve a computer vision model.
    """
    # Simulate a delay for a long-running process
    await asyncio.sleep(2)

    # In a real implementation, you would process the image file here.
    # For now, we'll just return a mock response.
    return ImageAnalysisResponse(
        description=f"A mock analysis of the image '{image.filename}'.",
        tags=["mock", "analysis", "placeholder"]
    )


class ProcurementOptimizer:
    """
    Handles the logic for finding the best procurement options based on user preferences,
    including constraints like a total budget.
    """

    def find_constrained_optimal_setup(
        self,
        detected_items: list[DetectedItem],
        candidates_map: dict[str, list[MarketCandidate]],
        preferences: UserPreferences,
        max_total_budget: float
    ) -> Solution | None:
        """
        Finds the optimal set of market candidates that satisfies a budget constraint.

        This method uses a recursive approach to explore all valid combinations of
        items, scoring each combination based on user preferences and selecting the
        best one that respects the budget.

        Args:
            detected_items: A list of items detected by the CV system.
            candidates_map: A dictionary mapping item names to lists of candidates.
            preferences: The user's preferences for price, delivery, and quality.
            max_total_budget: The maximum total cost for the entire procurement.

        Returns:
            A Solution object for the best valid combination, or None if no
            combination satisfies the budget.
        """
        # --- 1. Pre-computation: Normalize scores for all candidates ---
        # This is crucial. We normalize within each item category first.
        # This gives us a fair "attractiveness" score for each individual candidate.
        normalized_scores: dict[str, dict[str, float]] = {}
        for item in detected_items:
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

        def solve(item_index: int, current_combination: dict[str, MarketCandidate]):
            # Base case: If we have a candidate for every item, we have a full solution.
            if item_index == len(detected_items):
                # Calculate total cost for the current combination
                total_cost = sum(
                    c.price * next(item.quantity for item in detected_items if item.name == name)
                    for name, c in current_combination.items()
                )

                # Constraint check
                if total_cost > max_total_budget:
                    return

                # Score the complete solution by summing the pre-computed scores of its parts.
                total_score = sum(normalized_scores[name][c.name] for name, c in current_combination.items())

                if total_score > best_solution["score"]:
                    best_solution["score"] = total_score
                    best_solution["combination"] = current_combination.copy()
                return

            # Recursive step: Explore candidates for the current item.
            current_item = detected_items[item_index]
            for candidate in candidates_map.get(current_item.name, []):
                current_combination[current_item.name] = candidate
                solve(item_index + 1, current_combination)
                # Backtrack
                del current_combination[current_item.name]

        solve(0, {})

        # --- 3. Format Output ---
        if not best_solution["combination"]:
            return None

        final_selections = best_solution["combination"]
        total_cost = sum(c.price * next(item.quantity for item in detected_items if item.name == name) for name, c in final_selections.items())
        max_delivery_days = max(c.delivery_days for c in final_selections.values())

        return Solution(
            selections=final_selections,
            total_cost=total_cost,
            max_delivery_days=max_delivery_days,
        )


# --- Demonstration Block ---
if __name__ == "__main__":
    # 1. Mock CV and Scraper Data
    detected_items_data = [
        DetectedItem(name="Office Chair", quantity=10, target_material="Mesh"),
        DetectedItem(name="Desk", quantity=10)
    ]

    market_candidates_data = {
        "Office Chair": [
            MarketCandidate(name="CheapChair 3000", price=120.0, delivery_days=10, quality_score=0.6, url="http://example.com/cheap-chair"),
            MarketCandidate(name="SpeedyChair Express", price=250.0, delivery_days=2, quality_score=0.8, url="http://example.com/fast-chair"),
            MarketCandidate(name="QualiChair Pro", price=400.0, delivery_days=7, quality_score=0.95, url="http://example.com/quality-chair"),
        ],
        "Desk": [
            MarketCandidate(name="Budget Desk", price=200.0, delivery_days=14, quality_score=0.5, url="http://example.com/cheap-desk"),
            MarketCandidate(name="Rapid Desk", price=350.0, delivery_days=3, quality_score=0.7, url="http://example.com/fast-desk"),
        ]
    }

    optimizer = ProcurementOptimizer()

    # --- Scenario: Find the best OVERALL setup with a budget of $6000 ---
    # This budget is enough for (SpeedyChair, Rapid Desk) but not (QualiChair, Rapid Desk)
    print("--- Scenario: Balanced Preferences with Budget Constraint ($6000) ---")
    balanced_prefs = UserPreferences(price_weight=0.4, delivery_weight=0.3, quality_weight=0.3)
    budget_solution = optimizer.find_constrained_optimal_setup(
        detected_items_data,
        market_candidates_data,
        balanced_prefs,
        max_total_budget=6000.0
    )

    if budget_solution:
        print(f"Selected Chair: {budget_solution.selections['Office Chair'].name}")
        print(f"Selected Desk: {budget_solution.selections['Desk'].name}")
        print(f"Total Cost: ${budget_solution.total_cost:.2f}")
        print(f"Max Delivery Time: {budget_solution.max_delivery_days} days\n")
    else:
        print("No solution found within the given budget.\n")

    # --- Scenario: What if the budget is very tight? ---
    print("--- Scenario: Balanced Preferences with TIGHT Budget Constraint ($3500) ---")
    tight_budget_solution = optimizer.find_constrained_optimal_setup(
        detected_items_data,
        market_candidates_data,
        balanced_prefs,
        max_total_budget=3500.0
    )

    if tight_budget_solution:
        print(f"Selected Chair: {tight_budget_solution.selections['Office Chair'].name}")
        print(f"Selected Desk: {tight_budget_solution.selections['Desk'].name}")
        print(f"Total Cost: ${tight_budget_solution.total_cost:.2f}")
        print(f"Max Delivery Time: {tight_budget_solution.max_delivery_days} days\n")
    else:
        print("No solution found within the given budget.\n")

