# test_rule_engine.py
import json
import os
from rules.engine import AgriRuleEngine, RuleSeverity
from backend.coordinator import run_agrimind_pipeline

def test_agri_rule_engine():
    print("=== Testing AgriRuleEngine Unit Functionality ===")
    
    # 1. Load Rules from agri_rules.json
    rules_path = os.path.join("rules", "agri_rules.json")
    engine = AgriRuleEngine.from_file(rules_path)
    assert len(engine.rules) >= 4
    print(f"[PASS] Loaded {len(engine.rules)} baseline rules.")

    # 2. Test Weather Irrigation Interlock (> 10mm precipitation halts irrigation)
    state_rain = {
        "rain_forecast_next_24h_mm": 15.4,
        "soil_moisture_percent": 35.0,
        "irrigation_recommended": True
    }
    eval_res = engine.evaluate(state_rain)
    assert eval_res["has_violations"] is True
    assert eval_res["overrides"]["irrigation_recommended"] is False
    assert eval_res["overrides"]["irrigation_status"] == "LOCKED_BY_WEATHER_RULE"
    print(f"[PASS] Weather Irrigation Interlock triggered & overrode state correctly: {eval_res['violations'][0]['message']}")

    # 3. Test Critical Soil Drought Rule (<= 20%)
    state_drought = {
        "soil_moisture_percent": 12.5,
        "rain_forecast_next_24h_mm": 0.0
    }
    eval_drought = engine.evaluate(state_drought)
    assert eval_drought["has_violations"] is True
    assert any(v["action"] == "EMERGENCY_IRRIGATION_ALERT" for v in eval_drought["violations"])
    print(f"[PASS] Critical Soil Drought Rule evaluated correctly.")

    # 4. Test Disease Quarantine Trigger (confidence >= 0.85)
    state_disease = {
        "disease_confidence": 0.92
    }
    eval_disease = engine.evaluate(state_disease)
    assert eval_disease["has_violations"] is True
    assert eval_disease["overrides"]["quarantine_active"] is True
    print(f"[PASS] Disease Quarantine Protocol enforced correctly.")

    # 5. Test Full Coordinator Pipeline Execution
    print("\n=== Testing Coordinator Multi-Agent Pipeline with Rules ===")
    farmer_context = {
        "district": "Ludhiana",
        "crop": "Wheat",
        "soil_moisture_percent": 15.0, # Will trigger soil moisture depletion rule
        "nitrogen_deficit_percent": 30.0 # Will trigger NPK deficit rule
    }
    pipeline_result = run_agrimind_pipeline(farmer_context)
    print(f"Status: {pipeline_result['status']}")
    print(f"Has Rule Overrides: {pipeline_result['has_rule_overrides']}")
    print("Violations Triggered:")
    for v in pipeline_result["rule_alerts"]:
        print(f" - [{v['severity']}] {v['name']}: {v['message']}")

    print("\nAdvisory Report Sample:")
    print(pipeline_result["advisory_report"][:300] + "...")
    print("\nALL RULE ENGINE AND COORDINATOR TESTS PASSED!")

if __name__ == "__main__":
    test_agri_rule_engine()
