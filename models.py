from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Coordinate(BaseModel):
    latitude: float
    longitude: float

class FarmRequest(BaseModel):
    coordinates: List[Coordinate]
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    temperature_unit: Optional[str] = "celsius"

class DailySeries(BaseModel):
    dates: List[str]
    weather_code: List[int]
    temp_max: List[float]
    temp_min: List[float]
    temp_avg: List[float]
    rainfall: List[float]
    precip_probability: List[int]
    wind_speed: List[float]
    wind_gusts: List[float]
    et0: List[float]
    sunshine_duration: List[float]

class HourlySeries(BaseModel):
    dates: List[str]
    avg_temp: List[float]
    soil_moisture_surface: List[float]
    soil_moisture_root: List[float]
    daily_evapotranspiration: List[float]
    vpd: List[float]
    radiation: List[float]

class Timeseries(BaseModel):
    daily: DailySeries
    soil_and_temp: HourlySeries

class WeatherInsightsResponse(BaseModel):
    timeseries: Timeseries
    insights: Dict[str, Any]
