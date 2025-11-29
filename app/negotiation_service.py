import random
import copy
from typing import Dict, List

from .models import (
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
    FinalReport,
)
from .services import ProcurementOptimizer


class NegotiationService:
    """
    Mocks a service that negotiates prices with manufacturers via a Voice LLM.
    """

    def negotiate_price(self, candidate: MarketCandidate, logs: List[str]) -> float:
        """
        Simulates a negotiation call for a given market candidate.

        Args:
            candidate: The market candidate to negotiate for.
            logs: A list to append processing logs to.

        Returns:
            The potentially new, lower price.
        """
        logs.append(f"-> Calling manufacturer for '{candidate.name}' (Current Price: ${candidate.price:.2f})...")

        # 80% chance of a successful negotiation
        if random.random() > 0.2:
            # Apply a random discount between 5% and 15%
            discount_percentage = random.uniform(0.05, 0.15)
            new_price = candidate.price * (1 - discount_percentage)
            logs.append(f"   Success! Negotiated a {discount_percentage:.1%} discount. New price: ${new_price:.2f}")
            return new_price
        else:
            logs.append("   Failed. The manufacturer did not agree to a discount.")
            return candidate.price


class ProcurementOrchestrator:
    """
    Orchestrates the end-to-end procurement process, including optimization and negotiation.
    """

    def __init__(self):
        self.optimizer = ProcurementOptimizer()
        self.negotiator = NegotiationService()

    def run_full_process(
        self,
        detected_items: List[DetectedItem],
        candidates_map: Dict[str, List[MarketCandidate]],
        preferences: UserPreferences,
        max_total_budget: float,
    ) -> FinalReport | None:
        """
        Executes the full procurement workflow:
        1. Find an initial optimal solution.
        2. Negotiate prices for high-value items.
        3. Re-optimize with the new prices to find the final solution.

        Args:
            detected_items: A list of items needed.
            candidates_map: A map of available market candidates for each item.
            preferences: The user's preferences for scoring.
            max_total_budget: The budget constraint for the procurement.

        Returns:
            A FinalReport containing the comparison, or None if no initial solution is found.
        """
        logs: List[str] = []
        quantity_map = {item.name: item.quantity for item in detected_items}

        # --- Step 1: Find the Initial Optimal Solution ---
        logs.append("Running Initial Optimization...")
        initial_solution = self.optimizer.find_constrained_optimal_setup(
            detected_items, candidates_map, preferences, max_total_budget
        )

        if not initial_solution:
            logs.append("Could not find an initial solution within the budget.")
            # Cannot proceed, but can return a partial report if needed. For now, returning None.
            return None

        logs.append(f"Initial solution found with cost: ${initial_solution.total_cost:.2f}")

        # --- Step 2: Identify High-Value Targets for Negotiation ---
        logs.append("Starting Negotiation Phase...")
        negotiated_candidates_map = copy.deepcopy(candidates_map)

        candidate_lookup: Dict[str, MarketCandidate] = {
            cand.name: cand
            for category in negotiated_candidates_map.values()
            for cand in category
        }

        negotiation_targets = []
        for item_name, selected_candidate in initial_solution.selections.items():
            item_quantity = quantity_map.get(item_name, 1)
            item_total_cost = selected_candidate.price * item_quantity

            if item_total_cost / initial_solution.total_cost > 0.10:
                negotiation_targets.append(selected_candidate)
                logs.append(f"Identified '{selected_candidate.name}' as a high-value negotiation target.")

        if not negotiation_targets:
            logs.append("No high-value items identified for negotiation. Skipping.")

        # --- Step 3: Negotiate Prices ---
        for target in negotiation_targets:
            new_price = self.negotiator.negotiate_price(target, logs)
            if target.name in candidate_lookup:
                candidate_lookup[target.name].price = new_price

        # --- Step 4: Re-run Optimization with Negotiated Prices ---
        logs.append("Re-running Optimization with Negotiated Prices...")
        negotiated_solution = self.optimizer.find_constrained_optimal_setup(
            detected_items, negotiated_candidates_map, preferences, max_total_budget
        )

        if not negotiated_solution:
            logs.append("Could not find a solution after negotiation. This can happen if discounts were minimal. Falling back to original solution.")
            negotiated_solution = initial_solution

        # --- Step 5: Generate Final Report ---
        savings = initial_solution.total_cost - negotiated_solution.total_cost
        savings_percentage = (savings / initial_solution.total_cost) * 100 if initial_solution.total_cost > 0 else 0
        logs.append(f"Process complete. Total savings: ${savings:.2f} ({savings_percentage:.2f}%).")

        return FinalReport(
            original_solution=initial_solution,
            negotiated_solution=negotiated_solution,
            savings_amount=savings,
            savings_percentage=savings_percentage,
            processing_logs=logs,
        )


# --- Demonstration Block ---
if __name__ == "__main__":
    # 1. Mock Data (same as in services.py for consistency)
    detected_items_data = [
        DetectedItem(name="Office Chair", quantity=10),
        DetectedItem(name="Desk", quantity=10),
    ]

    market_candidates_data = {
        "Office Chair": [
            MarketCandidate(name="CheapChair 3000", price=120.0, delivery_days=10, quality_score=0.6, url="..."),
            MarketCandidate(name="SpeedyChair Express", price=250.0, delivery_days=2, quality_score=0.8, url="..."),
            MarketCandidate(name="QualiChair Pro", price=400.0, delivery_days=7, quality_score=0.95, url="..."),
        ],
        "Desk": [
            MarketCandidate(name="Budget Desk", price=200.0, delivery_days=14, quality_score=0.5, url="..."),
            MarketCandidate(name="Rapid Desk", price=350.0, delivery_days=3, quality_score=0.7, url="..."),
        ],
    }

    preferences_data = UserPreferences(price_weight=0.4, delivery_weight=0.3, quality_weight=0.3)
    budget = 6000.0

    # 2. Run the Orchestration
    orchestrator = ProcurementOrchestrator()
    final_report = orchestrator.run_full_process(
        detected_items_data, market_candidates_data, preferences_data, budget
    )

    # 3. Print the Final Report
    if final_report:
        print("\n" + "="*40)
        print("           Procurement Summary")
        print("="*40)
        print(f"Budget: ${budget:.2f}\n")

        print(f"Before Negotiation: ${final_report.original_solution.total_cost:.2f}")
        for item, cand in final_report.original_solution.selections.items():
            print(f"  - {item}: {cand.name} (${cand.price:.2f})")

        print(f"\nAfter Negotiation: ${final_report.negotiated_solution.total_cost:.2f}")
        for item, cand in final_report.negotiated_solution.selections.items():
            print(f"  - {item}: {cand.name} (${cand.price:.2f})")

        print("\n" + "-"*40)
        if final_report.savings_amount > 0:
            print(f"Total Savings: ${final_report.savings_amount:.2f} ({final_report.savings_percentage:.2f}%)")
        else:
            print("No savings were achieved in this run.")
        print("="*40)

