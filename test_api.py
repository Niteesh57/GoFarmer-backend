from fastapi.testclient import TestClient
import json
from main import app

client = TestClient(app)

def run_tests():
    print("Testing /api/v1/insights with Full Decision Engine ...")
    
    request_data = {
        "coordinates": [
            {"latitude": 52.50, "longitude": 13.40},
            {"latitude": 52.54, "longitude": 13.40},
            {"latitude": 52.54, "longitude": 13.45},
            {"latitude": 52.50, "longitude": 13.45}
        ],
        "temperature_unit": "celsius"
    }
    
    response = client.post("/api/v1/insights", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response successful!")
        data = response.json()
        adv = data['insights']['advanced_insights']
        
        print("\n--- BASIC METRICS ---")
        print(f"Moisture: {adv['moisture']['value']}% ({adv['moisture']['status']})")
        print(f"Humidity: {adv['air_humidity']['value']}% ({adv['air_humidity']['status']})")
        
        print("\n--- DECISION ENGINE ---")
        print(f"Irrigation: Next in {adv['irrigation_scheduler']['next_irrigation_days']} days, need {adv['irrigation_scheduler']['required_water_mm']}mm")
        print(f"Fertilizer: {adv['fertilizer_advisor']['status']} - {adv['fertilizer_advisor']['message']}")
        print(f"Spray: {adv['spray_advisor']['status']} - {adv['spray_advisor']['message']}")
        print(f"Yield Risk: {adv['yield_risk']['score']} ({adv['yield_risk']['rating']})")
        
        print("\n--- DASHBOARD ---")
        print(f"Summary Action: {adv['dashboard']['action']}")
    else:
        print("Response failed:")
        print(response.text)

if __name__ == "__main__":
    run_tests()
