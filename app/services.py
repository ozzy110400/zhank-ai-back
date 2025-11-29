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
    Handles the logic for finding the best procurement options based on user preferences.
    """

    def find_optimal_setup(
        self,
        detected_items: list[DetectedItem],
        candidates_map: dict[str, list[MarketCandidate]],
        preferences: UserPreferences
    ) -> Solution:
        """
        Finds the optimal set of market candidates for a list of detected items.

        Args:
            detected_items: A list of items detected by the CV system.
            candidates_map: A dictionary mapping item names to a list of available market candidates.
            preferences: The user's preferences for price, delivery, and quality.

        Returns:
            A Solution object containing the best selection of items.
        """
        selections: dict[str, MarketCandidate] = {}
        total_cost = 0.0
        max_delivery_days = 0

        for item in detected_items:
            candidates = candidates_map.get(item.name)
            if not candidates:
                continue

            # --- 1. Normalization ---
            # Extract values for normalization
            prices = [c.price for c in candidates]
            delivery_days = [c.delivery_days for c in candidates]
            quality_scores = [c.quality_score for c in candidates]

            # Get min/max for scaling. Add a small epsilon to avoid division by zero if all values are the same.
            min_price, max_price = min(prices), max(prices)
            min_days, max_days = min(delivery_days), max(delivery_days)
            min_quality, max_quality = min(quality_scores), max(quality_scores)

            epsilon = 1e-9

            # --- 2. Scoring ---
            best_candidate = None
            highest_score = -1.0

            for candidate in candidates:
                # Normalize cost metrics (lower is better).
                # A lower price should result in a higher score (closer to 1.0).
                norm_price = 1 - ((candidate.price - min_price) / (max_price - min_price + epsilon))

                # A shorter delivery time should result in a higher score.
                norm_delivery = 1 - ((candidate.delivery_days - min_days) / (max_days - min_days + epsilon))

                # Normalize utility metrics (higher is better).
                # A higher quality score remains high.
                norm_quality = (candidate.quality_score - min_quality) / (max_quality - min_quality + epsilon)

                # --- 3. Weighting ---
                # Calculate the final weighted score based on user preferences.
                # The weights determine the trade-off between cost, speed, and quality.
                final_score = (
                    (norm_price * preferences.price_weight) +
                    (norm_delivery * preferences.delivery_weight) +
                    (norm_quality * preferences.quality_weight)
                )

                if final_score > highest_score:
                    highest_score = final_score
                    best_candidate = candidate

            if best_candidate:
                selections[item.name] = best_candidate
                total_cost += best_candidate.price * item.quantity
                if best_candidate.delivery_days > max_delivery_days:
                    max_delivery_days = best_candidate.delivery_days

        return Solution(
            selections=selections,
            total_cost=total_cost,
            max_delivery_days=max_delivery_days
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

    # 2. Scenario 1: User prioritizes PRICE
    price_focused_prefs = UserPreferences(price_weight=0.8, delivery_weight=0.1, quality_weight=0.1)
    price_solution = optimizer.find_optimal_setup(detected_items_data, market_candidates_data, price_focused_prefs)

    print("--- Scenario: Price-Focused (Weight: 80%) ---")
    print(f"Selected Chair: {price_solution.selections['Office Chair'].name} (Price: ${price_solution.selections['Office Chair'].price})")
    print(f"Selected Desk: {price_solution.selections['Desk'].name} (Price: ${price_solution.selections['Desk'].price})")
    print(f"Total Cost: ${price_solution.total_cost:.2f}")
    print(f"Max Delivery Time: {price_solution.max_delivery_days} days\n")

    # 3. Scenario 2: User prioritizes DELIVERY SPEED
    delivery_focused_prefs = UserPreferences(price_weight=0.1, delivery_weight=0.8, quality_weight=0.1)
    delivery_solution = optimizer.find_optimal_setup(detected_items_data, market_candidates_data, delivery_focused_prefs)

    print("--- Scenario: Delivery-Focused (Weight: 80%) ---")
    print(f"Selected Chair: {delivery_solution.selections['Office Chair'].name} (Delivery: {delivery_solution.selections['Office Chair'].delivery_days} days)")
    print(f"Selected Desk: {delivery_solution.selections['Desk'].name} (Delivery: {delivery_solution.selections['Desk'].delivery_days} days)")
    print(f"Total Cost: ${delivery_solution.total_cost:.2f}")
    print(f"Max Delivery Time: {delivery_solution.max_delivery_days} days\n")

    # 4. Scenario 3: User prioritizes QUALITY
    quality_focused_prefs = UserPreferences(price_weight=0.1, delivery_weight=0.1, quality_weight=0.8)
    quality_solution = optimizer.find_optimal_setup(detected_items_data, market_candidates_data, quality_focused_prefs)

    print("--- Scenario: Quality-Focused (Weight: 80%) ---")
    print(f"Selected Chair: {quality_solution.selections['Office Chair'].name} (Quality: {quality_solution.selections['Office Chair'].quality_score})")
    print(f"Selected Desk: {quality_solution.selections['Desk'].name} (Quality: {quality_solution.selections['Desk'].quality_score})")
    print(f"Total Cost: ${quality_solution.total_cost:.2f}")
    print(f"Max Delivery Time: {quality_solution.max_delivery_days} days\n")

