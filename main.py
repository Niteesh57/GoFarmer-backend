from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import FarmRequest, WeatherInsightsResponse
from weather_service import fetch_weather_data
import traceback
import pandas as pd

app = FastAPI(title="Agri Weather Insights API", version="1.0.0")

# Add CORS middleware if needed for mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Agri Weather Insights API"}

@app.post("/api/v1/insights", response_model=WeatherInsightsResponse)
def get_insights(request: FarmRequest):
    try:
        # Calculate bounding box from coordinates
        if not request.coordinates:
            raise HTTPException(status_code=400, detail="Coordinates list cannot be empty")
            
        lats = [c.latitude for c in request.coordinates]
        lons = [c.longitude for c in request.coordinates]
        
        min_lat = min(lats)
        max_lat = max(lats)
        min_lon = min(lons)
        max_lon = max(lons)
        
        # If they only provided 1 coordinate, make the bounding box tiny but valid for that spot
        if min_lat == max_lat:
            max_lat += 0.01
        if min_lon == max_lon:
            max_lon += 0.01

        # Fetch weather data
        unit = request.temperature_unit or "celsius"
        
        # Parse dates if provided (DD-MM-YYYY -> YYYY-MM-DD)
        start_date_str = None
        end_date_str = None
        
        try:
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if request.start_date:
                start_dt = datetime.strptime(request.start_date, "%d-%m-%Y").date()
                # Open-Meteo forecast API supports up to 92 days of past data
                min_past = today - timedelta(days=92)
                if start_dt < min_past:
                    start_dt = min_past
                start_date_str = start_dt.strftime("%Y-%m-%d")
            
            if request.end_date:
                end_dt = datetime.strptime(request.end_date, "%d-%m-%Y").date()
                # Open-Meteo forecast API supports up to 15-16 days of forecast
                max_forecast = today + timedelta(days=15)
                if end_dt > max_forecast:
                    end_dt = max_forecast
                
                # Ensure end_date is not before start_date
                if start_date_str:
                    start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                    if end_dt < start_dt:
                        end_dt = start_dt
                        
                end_date_str = end_dt.strftime("%Y-%m-%d")
                
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=f"Invalid date format. Use DD-MM-YYYY: {str(ve)}")

        daily_df, hourly_df = fetch_weather_data(
            min_lat, max_lat, min_lon, max_lon, unit, 
            start_date=start_date_str, 
            end_date=end_date_str
        )
        
        # Explicitly filter to requested range to handle timezone overlaps or API defaults
        if start_date_str:
            start_ts = pd.to_datetime(start_date_str)
            daily_df = daily_df[daily_df['date'] >= start_ts]
            hourly_df = hourly_df[hourly_df['date'] >= start_ts]
        
        if end_date_str:
            end_ts = pd.to_datetime(end_date_str) + pd.Timedelta(days=1)
            daily_df = daily_df[daily_df['date'] < end_ts]
            hourly_df = hourly_df[hourly_df['date'] < end_ts]

        # Process analytics
        from insights_engine import FarmerWeatherAnalytics
        analyzer = FarmerWeatherAnalytics(unit=unit)
        result = analyzer.get_full_analysis(daily_df, hourly_df)
        
        return result
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
