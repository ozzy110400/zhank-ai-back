from fastapi.testclient import TestClient
from app.main import app

# Initialize the test client
client = TestClient(app)


def validate_end_to_end_procurement():
    """
    Runs an automated integration test on the /procure/optimize endpoint
    to validate the entire system before handoff.
    """
    print("--- Starting End-to-End System Validation ---")

    # 1. Define the mock payload (what the Frontend would send)
    test_payload = {
        "detected_items": [
            {"name": "Office Chair", "quantity": 10, "target_material": "Mesh"},
            {"name": "Standing Desk", "quantity": 5},
        ],
        "preferences": {
            "price_weight": 0.4,
            "delivery_weight": 0.3,
            "quality_weight": 0.3,
        },
        "budget": 7000.0,
    }
    print(f"Test Payload: Budget ${test_payload['budget']}, Items: 10 Office Chairs, 5 Standing Desks")

    # 2. Send a POST request to the endpoint
    print("\nSending request to /procure/optimize...")
    response = client.post("/procure/optimize", json=test_payload)

    # 3. Assert and print the response
    print(f"Response Status Code: {response.status_code}")
    assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    print("Assertion Passed: Status code is 200.")

    response_data = response.json()

    print("\n--- Results ---")
    original_cost = response_data["original_solution"]["total_cost"]
    negotiated_cost = response_data["negotiated_solution"]["total_cost"]
    savings = response_data["savings_amount"]

    print(f"Original Cost: ${original_cost:.2f}")
    print(f"Negotiated Cost: ${negotiated_cost:.2f}")
    print(f"Total Savings: ${savings:.2f}")

    print("\n--- Audit Logs (AI's Thought Process) ---")
    for log in response_data["processing_logs"]:
        print(f"- {log}")

    print("\n--- System Validation Complete ---")
    if savings > 0:
        print("SUCCESS: The system correctly optimized, negotiated, and reported savings.")
    else:
        print("NOTE: The system ran successfully, but no savings were achieved in this run.")


if __name__ == "__main__":
    validate_end_to_end_procurement()

