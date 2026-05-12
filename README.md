# GoFarmer Backend Service

A high-performance **FastAPI** backend powering the agronomic intelligence and weather analytics for the **GoFarmer** mobile frontend application. 

By aggregating hyperlocal meteorological data and calculating advanced soil/crop dynamics, this service acts as the central decision-support engine for modern smart farming.

---

## 🌟 What It Does

The backend integrates seamlessly with the **Open-Meteo API** to fetch past, current, and forecasted weather data for specific farm boundary coordinates. It processes complex environmental arrays into actionable agricultural insights:

### 📊 Comprehensive Timeseries Data
- **Daily Aggregates**: Maximum, minimum, and average temperatures, rainfall accumulation, precipitation probability, wind speed/gusts, solar radiation, and reference evapotranspiration ($ET_0$).
- **Hourly Telemetry**: Real-time multi-depth soil moisture modeling (surface zone `0-1cm` and root zone `9-27cm`), vapor pressure deficit (VPD), and shortwave radiation.

### 🧠 Advanced Agronomic Intelligence Engine
- **💧 Irrigation Scheduler**: Predicts the exact number of days until the soil reaches critical dryness and prescribes the required irrigation volume in millimeters.
- **🌱 Fertilizer Advisor**: Monitors upcoming precipitation thresholds to recommend optimal application windows or prompt delays to prevent runoff.
- **🚁 Spray Advisor**: Evaluates local wind speeds and rain forecasts to ensure pesticides and treatments are applied safely without drift or wash-off.
- **🐛 Pest Risk Assessment**: Combines heat and humidity matrices to detect periods of elevated insect pressure.
- **🌾 Crop-Stage Advisory**: Tracks optimal environmental safety metrics tailored to critical growth phases: **Germination**, **Flowering**, and **Harvesting**.

---

## 🤝 How It Helps the GoFarmer Frontend App

The GoFarmer React Native application depends on this API service (`POST /api/v1/insights`) to deliver dynamic, high-fidelity user experiences:

1. **Powers Dashboard Indicators**: Instantly populates easy-to-read status widgets (e.g., *"Safe to Spray"*, *"Delay Fertilizer"*, *"Good Moisture"*) directly on the farmer's mobile screen.
2. **Drives Interactive Visualizations**: Supplies perfectly structured time-series datasets enabling smooth chart rendering for soil moisture trends and temperature trajectories.
3. **Enhances On-Device AI Context**: Generates customized context strings and engineered prompts (`llm_prompt`) fed directly into the mobile app's local offline/multimodal AI assistant (CactusLM engine). This enables localized, voice-to-voice advisory responses in regional languages based on real-time ground truth.

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.12+**
- **Docker** (optional, for containerized runs)

### Local Installation & Running

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **API Documentation:**
   Once running, explore the interactive OpenAPI/Swagger documentation at:
   👉 `http://localhost:8000/docs`

### Running with Docker

Build and run the pre-configured lightweight container directly:

```bash
# Build the Docker image
docker build -t gofarmer-backend .

# Run the container
docker run -d -p 8000:8000 gofarmer-backend
```

---

## 📡 API Endpoint Reference

### `POST /api/v1/insights`
Accepts single coordinates or a bounding box polygon of the farm alongside dynamic date filters to compute targeted analytics.

**Sample Request Payload:**
```json
{
  "coordinates": [
    {"latitude": 12.9716, "longitude": 77.5946}
  ],
  "start_date": "10-05-2026",
  "end_date": "20-05-2026",
  "temperature_unit": "celsius"
}
```

**Sample Response Output:**
Returns deep granular data separated into raw `timeseries` arrays and structured `insights` metadata ready for frontend consumption.
