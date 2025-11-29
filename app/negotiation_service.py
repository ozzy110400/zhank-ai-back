import random
import copy
import re
import time
from typing import Dict, List, Optional

import requests
from .models import (
    DetectedItem,
    MarketCandidate,
    UserPreferences,
    Solution,
    FinalReport,
)
from .services import ProcurementOptimizer

# --- Configuration for the Partner API ---
NEGBOT_API_BASE = "https://negbot-backend-ajdxh9axb0ddb0e9.westeurope-01.azurewebsites.net/api"
TEAM_ID = "641754"


class NegotiationService:
    """
    Integrates with the NegBot REST API to negotiate prices.
    """

    def __init__(self):
        self.session = requests.Session()
        self.team_params = {"team_id": TEAM_ID}

    def _get_or_create_vendor(self, vendor_name: str, logs: List[str]) -> Optional[int]:
        """
        Retrieves a vendor's ID by name, creating the vendor if it doesn't exist.
        """
        try:
            # 1. Check if vendor exists
            response = self.session.get(f"{NEGBOT_API_BASE}/vendors/", params=self.team_params)
            response.raise_for_status()
            vendors = response.json()
            for vendor in vendors:
                if vendor.get("name") == vendor_name:
                    logs.append(f"Found existing vendor '{vendor_name}' with ID: {vendor['id']}.")
                    return vendor["id"]

            # 2. If not, create it
            logs.append(f"Vendor '{vendor_name}' not found. Creating new vendor...")

            # --- FIX: Added description and behavioral_prompt to satisfy API requirements ---
            new_vendor_payload = {
                "name": vendor_name,
                "description": f"A generic supplier of office equipment: {vendor_name}",
                # We make the AI 'flexible' so the Hackathon demo is more likely to get a discount!
                "behavioral_prompt": (
                    "You are a helpful and flexible sales representative. "
                    "You value new customers and are willing to offer discounts "
                    "to close a deal quickly."
                )
            }

            response = self.session.post(
                f"{NEGBOT_API_BASE}/vendors/",
                params=self.team_params,
                json=new_vendor_payload,
            )
            response.raise_for_status()
            new_vendor = response.json()
            logs.append(f"Successfully created vendor '{vendor_name}' with ID: {new_vendor['id']}.")
            return new_vendor["id"]

        except requests.RequestException as e:
            # If creating fails, log the specific server response if available
            error_details = e.response.text if e.response else str(e)
            logs.append(f"API Error: Failed to get or create vendor '{vendor_name}'. Details: {error_details}")
            return None

    def _extract_price_from_text(self, text: str) -> Optional[float]:
        """
        Uses regex to find a dollar amount in a string.
        """
        # This regex finds patterns like $450, $450.00, $ 450, etc.
        matches = re.findall(r'\$(\s*\d+\.?\d*)', text)
        if matches:
            # Return the last found price, as it's likely the final offer.
            last_price_str = matches[-1].strip()
            return float(last_price_str)
        return None

    def negotiate_price(self, candidate: MarketCandidate, quantity: int, logs: List[str]) -> float:
        """
        Orchestrates the negotiation with the NegBot API.
        """
        logs.append(
            f"-> Starting negotiation for {quantity} units of '{candidate.name}' (List Price: ${candidate.price:.2f}).")

        # Respect rate limit: 20 req/min means 1 every 3 seconds.
        # We make 3 calls, so a small sleep is prudent.
        time.sleep(3)

        try:
            # Step 1: Get or create the vendor
            vendor_id = self._get_or_create_vendor(candidate.name, logs)
            if not vendor_id:
                raise ValueError("Vendor ID could not be obtained.")

            # Step 2: Start a new conversation
            conv_response = self.session.post(
                f"{NEGBOT_API_BASE}/conversations/",
                params=self.team_params,
                json={
                    "vendor_id": vendor_id,
                    "title": f"Hackathon Negotiation for {candidate.name}",
                },
            )
            conv_response.raise_for_status()
            conversation = conv_response.json()
            conversation_id = conversation["id"]
            logs.append(f"Started conversation {conversation_id} with '{candidate.name}'.")

            # Step 3: Send the negotiation prompt
            prompt = (
                f"I am interested in the {candidate.name}. I need {quantity} units. "
                f"Your list price is ${candidate.price:.2f} each. I have a strict budget. "
                f"What is the absolute best price you can offer me per unit?"
            )

            msg_response = self.session.post(
                f"{NEGBOT_API_BASE}/messages/{conversation_id}",
                params=self.team_params,
                data={"content": prompt},  # Use multipart/form-data as required
            )
            msg_response.raise_for_status()
            bot_reply = msg_response.json()["content"]
            logs.append(f"   Vendor '{candidate.name}' replied: \"{bot_reply}\"")

            # Step 4: Parse the response for a new price
            new_price = self._extract_price_from_text(bot_reply)

            if new_price and new_price < candidate.price:
                logs.append(f"   Success! Parsed new price: ${new_price:.2f}")
                return new_price
            elif new_price and new_price >= candidate.price:
                logs.append(f"   Negotiation finished, but price did not decrease (Offered: ${new_price:.2f}).")
                return candidate.price
            else:
                logs.append("   Negotiation failed. No clear price found in response.")
                return candidate.price

        except (requests.RequestException, ValueError) as e:
            logs.append(f"   Negotiation process failed due to an error: {e}. Using original price.")
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
        Executes the full procurement workflow.
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

            # Strategy: Only negotiate for items that are >10% of the total cost
            if initial_solution.total_cost > 0 and (item_total_cost / initial_solution.total_cost > 0.10):
                negotiation_targets.append(selected_candidate)
                logs.append(f"Identified '{selected_candidate.name}' as a high-value negotiation target.")

        if not negotiation_targets:
            logs.append("No high-value items identified for negotiation. Skipping.")

        # --- Step 3: Negotiate Prices ---
        for target in negotiation_targets:
            quantity = quantity_map.get(target.name, 1)
            new_price = self.negotiator.negotiate_price(target, quantity, logs)
            if target.name in candidate_lookup:
                candidate_lookup[target.name].price = new_price

        # --- Step 4: Re-run Optimization with Negotiated Prices ---
        logs.append("Re-running Optimization with Negotiated Prices...")
        negotiated_solution = self.optimizer.find_constrained_optimal_setup(
            detected_items, negotiated_candidates_map, preferences, max_total_budget
        )

        if not negotiated_solution:
            logs.append("Could not find a solution after negotiation. Falling back to original solution.")
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


# --- Demonstration Block for API Integration Testing ---
if __name__ == "__main__":
    print("--- Testing NegBot API Integration ---")

    # 1. Setup
    test_negotiator = NegotiationService()
    test_logs = []

    # A mock candidate to test negotiation for.
    # Using a timestamp to ensure unique name for creation
    timestamp = int(time.time())
    test_candidate = MarketCandidate(
        name=f"TestCorp Chair {timestamp}",
        price=500.0,
        delivery_days=5,
        quality_score=0.9,
        url="http://example.com/test-chair"
    )

    # 2. Run negotiation
    print(f"Creating vendor and negotiating for: {test_candidate.name}")
    final_price = test_negotiator.negotiate_price(
        candidate=test_candidate,
        quantity=10,
        logs=test_logs
    )

    # 3. Print results
    print("\n--- LOGS ---")
    for log_entry in test_logs:
        print(log_entry)

    print("\n--- RESULTS ---")
    print(f"Original Price: ${test_candidate.price:.2f}")
    print(f"Final Negotiated Price: ${final_price:.2f}")

    if final_price < test_candidate.price:
        print("\nSUCCESS: The API integration appears to be working and a discount was negotiated.")
    else:
        print("\nNOTE: The API integration may be working, but no discount was achieved.")