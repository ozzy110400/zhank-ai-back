import requests
import time
import json
import base64
import os  # <--- Added import

# Configuration
API_URL = "http://127.0.0.1:8000"
HEADERS = {"Content-Type": "application/json"}


def print_step(title):
    print(f"\n{'=' * 60}")
    print(f"STEP: {title}")
    print(f"{'=' * 60}")
    time.sleep(1.5)


def frontend_action(action):
    print(f"\n👤 [FRONTEND USER]: {action}")
    time.sleep(1.0)


def backend_response(response):
    print(f"🤖 [BACKEND]: {response}")
    time.sleep(0.5)


# --- NEW FUNCTION FOR AUDIO ---
def play_audio_from_base64(b64_string):
    try:
        # Decode bytes
        audio_data = base64.b64decode(b64_string)
        filename = "vendor_reply.mp3"

        # Save to file
        with open(filename, "wb") as f:
            f.write(audio_data)

        print(f"   🔊 Playing audio ({len(b64_string)} bytes)...")

        # Try to open with default player (Linux specific since you are on /home/dias)
        # If you were on Mac you'd use 'afplay', on Windows 'start'
        os.system(f"xdg-open {filename}")

        # Alternative: if xdg-open opens a window and annoys you,
        # try installing mpg123 (sudo apt install mpg123) and use:
        # os.system(f"mpg123 {filename}")

    except Exception as e:
        print(f"   ❌ Could not play audio: {e}")


def run_demo():
    print("🚀 STARTING PROCUREMENT CO-PILOT DEMO")

    # --- STEP 1: Image Analysis (Mocked Handoff) ---
    print_step("1. Image Upload & Requirement Extraction")
    frontend_action("Uploading 'new_office.jpg'...")

    detected_items = [
        {"name": "Office Chair", "quantity": 10, "target_material": "Mesh"},
        {"name": "Standing Desk", "quantity": 5}
    ]

    preferences = {
        "price_weight": 0.5,
        "delivery_weight": 0.25,
        "quality_weight": 0.25
    }
    budget = 8000.0

    backend_response(f"Identified items: {len(detected_items)} types.")
    backend_response(f"User Budget: ${budget}")

    # --- STEP 2: Initial Search & Optimization ---
    print_step("2. Search & Initial Optimization")
    frontend_action("Clicking 'Find Best Options' button...")

    search_payload = {
        "detected_items": detected_items,
        "preferences": preferences,
        "budget": budget
    }

    response = requests.post(f"{API_URL}/procure/search", json=search_payload)
    if response.status_code != 200:
        print(f"Error: {response.text}")
        return

    search_data = response.json()
    initial_solution = search_data["initial_solution"]
    all_candidates = search_data["all_candidates"]

    # Display what the frontend would show
    print("\n   --- Results Displayed on UI ---")
    total_cost = initial_solution["total_cost"]
    print(f"   💰 Optimal Total Cost: ${total_cost:.2f}")

    target_item_name = "Office Chair"
    selected_chair = initial_solution["selections"][target_item_name]

    print(f"   🪑 Selected Chair: {selected_chair['name']} (${selected_chair['price']})")
    print(f"   📦 Delivery: {selected_chair['delivery_days']} days")

    # --- STEP 3: Start Negotiation ---
    print_step("3. User Initiates Negotiation")
    frontend_action(f"Calculated cost is too high. Clicking 'Negotiate' on {selected_chair['name']}...")

    neg_start_payload = {"candidate_name": selected_chair["name"]}
    response = requests.post(f"{API_URL}/negotiate/start", json=neg_start_payload)
    conversation_id = response.json()["conversation_id"]

    backend_response(f"Conversation started (ID: {conversation_id}). Chat window opens.")

    # --- STEP 4: Sending a Message ---
    print_step("4. Interactive Chat (Voice + Text)")
    message = "I need 10 units. I have a quote from a competitor for $280. Can you beat it?"
    frontend_action(f"Typing: '{message}'")
    frontend_action("Sending message...")

    msg_payload = {
        "conversation_id": conversation_id,
        "message_content": message
    }

    start_time = time.time()
    response = requests.post(f"{API_URL}/negotiate/message", json=msg_payload)
    latency = time.time() - start_time

    msg_data = response.json()
    vendor_text = msg_data["text_response"]
    audio_b64 = msg_data["audio_base64"]
    parsed_price = msg_data["parsed_new_price"]

    print(f"\n🏢 [VENDOR AGENT] (Latency: {latency:.2f}s):")
    print(f"   \"{vendor_text}\"")

    if audio_b64:
        # --- NEW CALL TO PLAY AUDIO ---
        play_audio_from_base64(audio_b64)

    if parsed_price:
        backend_response(f"Price Drop Detected! New Price: ${parsed_price}")
    else:
        print("   (No price change detected in this turn)")
        # Force a mock price for the demo if the AI was stubborn
        parsed_price = 280.0
        print(f"   [DEMO OVERRIDE]: Simulating successful negotiation to ${parsed_price}")

    # --- STEP 5: Recalculation ---
    print_step("5. User Accepts Deal & Recalculates")
    frontend_action(f"Clicking 'Accept ${parsed_price}' button...")

    for cand in all_candidates[target_item_name]:
        if cand["name"] == selected_chair["name"]:
            cand["price"] = parsed_price
            print(f"   (Frontend state updated: {cand['name']} price set to {cand['price']})")

    recalc_payload = {
        "detected_items": detected_items,
        "candidates_map": all_candidates,
        "preferences": preferences,
        "budget": budget,
        "fixed_items": {target_item_name: selected_chair["name"]}
    }

    response = requests.post(f"{API_URL}/procure/recalculate", json=recalc_payload)
    recalc_data = response.json()
    new_solution = recalc_data["initial_solution"]

    print("\n   --- Updated Results on UI ---")
    new_total = new_solution["total_cost"]
    savings = total_cost - new_total

    print(f"   💰 New Total Cost: ${new_total:.2f}")
    print(f"   📉 Savings: ${savings:.2f}")

    final_chair = new_solution["selections"][target_item_name]
    print(f"   🔒 Locked Item: {final_chair['name']} at ${final_chair['price']}")

    if final_chair["price"] == parsed_price:
        print("\n✅ DEMO SUCCESS: System optimized around the negotiated price.")
    else:
        print("\n❌ DEMO FAIL: Optimizer ignored the fixed price.")


if __name__ == "__main__":
    try:
        run_demo()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Backend.")
        print("Make sure it's running: 'uvicorn app.main:app --reload'")