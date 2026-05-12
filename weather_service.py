import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
from datetime import datetime, timedelta

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def fetch_weather_data(min_lat: float, max_lat: float, min_lon: float, max_lon: float, temperature_unit: str = "celsius", start_date: str = None, end_date: str = None):
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Calculate center point
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    params = {
        "latitude": center_lat,
        "longitude": center_lon,
        "temperature_unit": temperature_unit,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "rain_sum",
            "showers_sum",
            "precipitation_hours",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "et0_fao_evapotranspiration",
            "sunshine_duration"
        ],
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "precipitation",
            "precipitation_probability",
            "vapor_pressure_deficit",
            "shortwave_radiation",
            "visibility",
            "soil_moisture_0_to_1cm",
            "soil_moisture_9_to_27cm",
            "soil_temperature_6cm",
            "evapotranspiration"
        ],
        "timezone": "auto"
    }

    if start_date and end_date:
        params["start_date"] = start_date
        params["end_date"] = end_date
    else:
        params["past_days"] = 15
        params["forecast_days"] = 15

    responses = openmeteo.weather_api(url, params=params)
    
    if not responses:
        raise Exception("No weather data found")
        
    response = responses[0]
    
    # Process daily data
    daily = response.Daily()
    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s"),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    # Daily variables indices (matching order in 'daily' list)
    daily_data["weather_code"] = daily.Variables(0).ValuesAsNumpy()
    daily_data["temperature_2m_max"] = daily.Variables(1).ValuesAsNumpy()
    daily_data["temperature_2m_min"] = daily.Variables(2).ValuesAsNumpy()
    daily_data["precipitation_sum"] = daily.Variables(3).ValuesAsNumpy()
    daily_data["precipitation_probability_max"] = daily.Variables(7).ValuesAsNumpy()
    daily_data["wind_speed_10m_max"] = daily.Variables(8).ValuesAsNumpy()
    daily_data["wind_gusts_10m_max"] = daily.Variables(9).ValuesAsNumpy()
    daily_data["et0_fao_evapotranspiration"] = daily.Variables(10).ValuesAsNumpy()
    daily_data["sunshine_duration"] = daily.Variables(11).ValuesAsNumpy()
    
    daily_df = pd.DataFrame(data = daily_data)
    
    # Process hourly data
    hourly = response.Hourly()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s"),
        end =  pd.to_datetime(hourly.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    # Hourly variables indices (matching order in 'hourly' list)
    hourly_data["temperature_2m"] = hourly.Variables(0).ValuesAsNumpy()
    hourly_data["relative_humidity_2m"] = hourly.Variables(1).ValuesAsNumpy()
    hourly_data["dew_point_2m"] = hourly.Variables(2).ValuesAsNumpy()
    hourly_data["precipitation"] = hourly.Variables(3).ValuesAsNumpy()
    hourly_data["precipitation_probability"] = hourly.Variables(4).ValuesAsNumpy()
    hourly_data["vapor_pressure_deficit"] = hourly.Variables(5).ValuesAsNumpy()
    hourly_data["shortwave_radiation"] = hourly.Variables(6).ValuesAsNumpy()
    hourly_data["visibility"] = hourly.Variables(7).ValuesAsNumpy()
    hourly_data["soil_moisture_0_to_1cm"] = hourly.Variables(8).ValuesAsNumpy()
    hourly_data["soil_moisture_9_to_27cm"] = hourly.Variables(9).ValuesAsNumpy()
    hourly_data["soil_temperature_6cm"] = hourly.Variables(10).ValuesAsNumpy()
    hourly_data["evapotranspiration"] = hourly.Variables(11).ValuesAsNumpy()
    
    hourly_df = pd.DataFrame(data = hourly_data)
    
    return daily_df, hourly_df
