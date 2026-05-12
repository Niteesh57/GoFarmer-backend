from fastapi.testclient import TestClient
import json
from main import app

client = TestClient(app)

def run_tests():
    print("Testing /api/v1/insights with Fahrenheit ...")
    
    request_data = {
        "coordinates": [
            {"latitude": 52.50, "longitude": 13.40}
        ],
        "temperature_unit": "fahrenheit"
    }
    
    response = client.post("/api/v1/insights", json=request_data)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Response successful!")
        data = response.json()
        
        print("\nTimeseries Daily Temp Max (first 5, should be F):", data['timeseries']['daily']['temp_max'][:5])
        
        print("\nAdvanced Insights:")
        adv = data['insights']['advanced_insights']
        print(f"- Soil Temperature: {adv['soil_temperature']['avg_soil_temp']} F")
        
        print("\nLLM Prompt snippet:")
        print(data['insights']['llm_prompt'][:100] + "...")
    else:
        print("Response failed:")
        print(response.text)

if __name__ == "__main__":
    run_tests()
