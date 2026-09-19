# test_guardrail.py
from fastapi.testclient import TestClient
from app import app
from agri_guardrail import MandatoryRuleGuard

client = TestClient(app)

def test_guardrail_unit():
    print("=== Testing MandatoryRuleGuard Unit Logic ===")
    guard = MandatoryRuleGuard("rules/agri_rules.json")

    # Test telemetry with heavy rain forecast
    telemetry = {
        "rain_forecast_next_24h_mm": 18.0,
        "soil_moisture_percent": 28.0
    }
    overrides, directives = guard.evaluate_and_enforce(telemetry)
    print("Overrides:", overrides)
    print("Directives:", directives)

    assert overrides.get("irrigation_recommended") is False
    assert overrides.get("irrigation_status") == "LOCKED_BY_WEATHER_RULE"
    assert len(directives) >= 1
    assert "HALT_IRRIGATION" in directives[0]
    print("[PASS] Unit guardrail evaluation verified!")

def test_guarded_chat_endpoint():
    print("\n=== Testing Guarded Chat API Endpoint ===")
    payload = {
        "session_id": "guard_test_session_1",
        "user_prompt": "Can I run my scheduled canal irrigation for my wheat field today?",
        "telemetry": {
            "rain_forecast_next_24h_mm": 22.5,
            "soil_moisture_percent": 30.0
        }
    }

    response = client.post("/api/v1/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    print("Reply:\n", data["reply"])
    print("\nEnforced Rules:", data["enforced_rules"])
    print("Active Overrides:", data["active_overrides"])

    assert len(data["enforced_rules"]) > 0
    assert data["active_overrides"].get("irrigation_recommended") is False
    print("\n[PASS] Guarded Chat API successfully enforced agronomic rules on LLM output!")

if __name__ == "__main__":
    test_guardrail_unit()
    test_guarded_chat_endpoint()
