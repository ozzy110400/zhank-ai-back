import requests
import os
import time
import json
import base64
import webbrowser

# Configuration
API_URL = "http://127.0.0.1:8000"
IMAGE_PATH = "photo.jpg"  # Make sure this file exists!


def print_step(title):
    print(f"\n{'=' * 70}")
    print(f"STEP: {title}")
    print(f"{'=' * 70}")
    time.sleep(1)


def play_audio_from_base64(b64_string):
    """Saves audio to a temp file and attempts to play it."""
    try:
        audio_data = base64.b64decode(b64_string)
        filename = "vendor_reply.mp3"
        with open(filename, "wb") as f:
            f.write(audio_data)

        print(f"   🔊 [Audio] Saved to {filename}. Playing...")
        # Cross-platform open command
        if os.name == 'nt':  # Windows
            os.system(f"start {filename}")
        elif os.uname().sysname == 'Darwin':  # Mac
            os.system(f"afplay {filename}")
        else:  # Linux
            os.system(f"xdg-open {filename}")
    except Exception as e:
        print(f"   ⚠️ Could not play audio automatically: {e}")


def test_product_image_retrieval(product_name):
    """Calls the image endpoint and opens the result in the browser."""
    print(f"   🔎 Fetching image for product: '{product_name}'...")
    try:
        response = requests.get(f"{API_URL}/product/image", params={"name": product_name})

        if response.status_code == 200:
            image_url = response.json().get("image_url")
            print(f"   🖼️  Image Found: {image_url}")
            print(f"   🚀 Opening in browser...")
            webbrowser.open(image_url)
        else:
            print(f"   ❌ Failed to get image. Status: {response.status_code}")

    except Exception as e:
        print(f"   ⚠️ Error fetching image: {e}")


def run_full_validation():
    print("🚀 STARTING FULL SYSTEM INTEGRATION TEST")

    # --- Check for Image ---
    if not os.path.exists(IMAGE_PATH):
        print(f"❌ Error: Could not find '{IMAGE_PATH}' in the root directory.")
        print("Please place a .jpg file named 'photo.jpg' here and try again.")
        return

    # --- STEP 1: Upload & Analyze Image (OpenAI) ---
    print_step("1. Image Upload & Analysis (OpenAI GPT-4o)")
    print(f"   Uploading '{IMAGE_PATH}'...")

    try:
        with open(IMAGE_PATH, "rb") as f:
            files = {"image": (IMAGE_PATH, f, "image/jpeg")}
            response = requests.post(f"{API_URL}/upload-image/", files=files)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Backend. Is 'uvicorn' running?")
        return

    if response.status_code != 200:
        print(f"❌ Error Analysis Failed: {response.text}")
        return

    analysis_data = response.json()
    detected_items = analysis_data["detected_items"]

    print(f"   ✅ Analysis Success!")
    print(f"   📝 Description: {analysis_data['description']}")
    print(f"   🏷️  Tags: {analysis_data['tags']}")
    print(f"   📦 Detected {len(detected_items)} Items:")
    for item in detected_items:
        print(f"      - {item['quantity']}x {item['name']} ({item.get('target_material') or 'Any'})")

    if not detected_items:
        print("⚠️ No items detected. Cannot proceed with optimization.")
        return

    # --- STEP 2: Procurement Search ---
    print_step("2. Search & Initial Optimization")

    preferences = {
        "price_weight": 0.5,
        "delivery_weight": 0.3,
        "quality_weight": 0.2
    }
    budget = 10000.0

    search_payload = {
        "detected_items": detected_items,
        "preferences": preferences,
        "budget": budget
    }

    response = requests.post(f"{API_URL}/procure/search", json=search_payload)
    assert response.status_code == 200, f"Search Failed: {response.text}"
    search_data = response.json()

    initial_solution = search_data["initial_solution"]
    all_candidates = search_data["all_candidates"]

    if not initial_solution:
        print("⚠️ No solution found within budget.")
        return

    print(f"   💰 Initial Optimal Cost: ${initial_solution['total_cost']:.2f}")

    # Pick the first item to negotiate
    target_item_name = list(initial_solution["selections"].keys())[0]
    selected_candidate = initial_solution["selections"][target_item_name]

    print(f"   🎯 Target for Negotiation: {selected_candidate['name']}")
    print(f"      Current Price: ${selected_candidate['price']}")

    # --- STEP 2.5: Test Image Retrieval ---
    print_step(f"2b. Visual Check: Fetching Image for {selected_candidate['name']}")
    test_product_image_retrieval(selected_candidate["name"])

    # --- STEP 3: Negotiation ---
    print_step(f"3. Negotiating for {selected_candidate['name']}")

    # 3a. Start Conversation
    start_payload = {"candidate_name": selected_candidate["name"]}
    response = requests.post(f"{API_URL}/negotiate/start", json=start_payload)
    assert response.status_code == 200
    conversation_id = response.json()["conversation_id"]
    print(f"   💬 Conversation Started (ID: {conversation_id})")

    # 3b. Send Message
    user_msg = f"I need to buy {next(i['quantity'] for i in detected_items if i['name'] == target_item_name)} units. I have a lower quote. Can you beat it?"
    print(f"   👤 User: '{user_msg}'")

    msg_payload = {"conversation_id": conversation_id, "message_content": user_msg}
    response = requests.post(f"{API_URL}/negotiate/message", json=msg_payload)
    assert response.status_code == 200
    msg_data = response.json()

    print(f"   🤖 Vendor: \"{msg_data['text_response'][:100]}...\"")

    if msg_data["audio_base64"]:
        play_audio_from_base64(msg_data["audio_base64"])

    parsed_price = msg_data["parsed_new_price"]

    if not parsed_price:
        print("   ⚠️ No price drop detected. Forcing a demo price for Step 4.")
        parsed_price = selected_candidate["price"] * 0.9  # Force 10% drop

    print(f"   🏷️  New Negotiated Price: ${parsed_price:.2f}")

    # --- STEP 4: Recalculate ---
    print_step("4. Recalculate with Locked Price")

    # Update local state
    for cand in all_candidates[target_item_name]:
        if cand["name"] == selected_candidate["name"]:
            cand["price"] = parsed_price

    recalc_payload = {
        "detected_items": detected_items,
        "candidates_map": all_candidates,
        "preferences": preferences,
        "budget": budget,
        "fixed_items": {target_item_name: selected_candidate["name"]}
    }

    response = requests.post(f"{API_URL}/procure/recalculate", json=recalc_payload)
    assert response.status_code == 200
    recalc_data = response.json()

    new_solution = recalc_data["initial_solution"]
    print(f"   💰 New Total Cost: ${new_solution['total_cost']:.2f}")

    savings = initial_solution['total_cost'] - new_solution['total_cost']
    print(f"   📉 Total Savings: ${savings:.2f}")

    # Verify Lock
    final_selection = new_solution["selections"][target_item_name]
    if final_selection["price"] == parsed_price:
        print("\n✅ SUCCESS: System integrated correctly from Image to Negotiation!")
    else:
        print("\n❌ FAIL: Recalculation did not use the negotiated price.")


if __name__ == "__main__":
    run_full_validation()