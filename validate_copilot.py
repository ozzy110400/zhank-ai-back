import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def validate_copilot_workflow():
    print("--- Starting Co-Pilot Workflow Validation ---")

    # --- Step 1: Initial Search ---
    print("\n1. Running Initial Search...")
    search_payload = {
        "detected_items": [
            {"name": "Office Chair", "quantity": 10},
            {"name": "Desk", "quantity": 5},
        ],
        "preferences": {"price_weight": 0.5, "delivery_weight": 0.25, "quality_weight": 0.25},
        "budget": 8000.0,
    }

    response = client.post("/procure/search", json=search_payload)
    assert response.status_code == 200
    search_data = response.json()

    # Extract the name of the chair selected by the AI
    selected_chair = search_data["initial_solution"]["selections"]["Office Chair"]
    print(f"   AI Selected: {selected_chair['name']} at ${selected_chair['price']}")

    # --- Step 2: Start Negotiation ---
    print(f"\n2. Starting Negotiation for '{selected_chair['name']}'...")
    neg_start_payload = {"candidate_name": selected_chair["name"]}
    response = client.post("/negotiate/start", json=neg_start_payload)
    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    print(f"   Conversation ID: {conversation_id}")

    # --- Step 3: Send Message ---
    print("\n3. Sending Negotiation Message...")
    msg_payload = {
        "conversation_id": conversation_id,
        "message_content": "I need 10 units. I have a quote for $300. Can you beat it?"
    }
    response = client.post("/negotiate/message", json=msg_payload)
    assert response.status_code == 200
    msg_data = response.json()

    print(f"   Vendor Reply: {msg_data['text_response'][:60]}...")
    if msg_data['audio_base64']:
        print("   [Audio Data Received]")
    else:
        print("   [WARNING: No Audio Data]")

    # --- Step 4: Simulate Recalculation (Locking the Price) ---
    print("\n4. Recalculating with Fixed Price...")

    # Let's pretend we successfully negotiated the chair to $300 (even if API didn't give it)
    new_price = 300.0

    # Create the data for recalculation:
    # 1. Get the original candidates
    all_candidates = search_data["all_candidates"]

    # 2. Update the price of the specific chair in the list
    for cand in all_candidates["Office Chair"]:
        if cand["name"] == selected_chair["name"]:
            cand["price"] = new_price

    # 3. Create request payload
    recalc_payload = {
        "detected_items": search_payload["detected_items"],
        "candidates_map": all_candidates,
        "preferences": search_payload["preferences"],
        "budget": search_payload["budget"],
        # THIS IS THE KEY: We force the optimizer to pick this chair
        "fixed_items": {"Office Chair": selected_chair["name"]}
    }

    response = client.post("/procure/recalculate", json=recalc_payload)
    assert response.status_code == 200
    recalc_data = response.json()

    new_total = recalc_data["initial_solution"]["total_cost"]
    print(f"   New Total Cost: ${new_total:.2f}")

    # Verify the chair is the one we fixed
    final_chair = recalc_data["initial_solution"]["selections"]["Office Chair"]
    assert final_chair["name"] == selected_chair["name"]
    assert final_chair["price"] == new_price
    print("   SUCCESS: Optimizer respected the fixed item and updated price.")


if __name__ == "__main__":
    validate_copilot_workflow()