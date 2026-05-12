import pandas as pd
import numpy as np
from datetime import datetime

class FarmerWeatherAnalytics:
    def __init__(self, unit: str = "celsius"):
        self.unit = unit

    def to_u(self, c):
        return float(c * 9/5 + 32) if self.unit == "fahrenheit" else float(c)

    def build_timeseries(self, daily_df: pd.DataFrame, hourly_df: pd.DataFrame):
        daily_df = daily_df.fillna(0)
        hourly_df = hourly_df.fillna(0)

        # Calculate temp_avg for the timeseries
        daily_df['temp_avg'] = (daily_df["temperature_2m_max"] + daily_df["temperature_2m_min"]) / 2

        daily_series = {
            "dates": daily_df["date"].dt.strftime("%Y-%m-%d").tolist(),
            "weather_code": daily_df["weather_code"].astype(int).tolist(),
            "temp_max": daily_df["temperature_2m_max"].astype(float).round(2).tolist(),
            "temp_min": daily_df["temperature_2m_min"].astype(float).round(2).tolist(),
            "temp_avg": daily_df["temp_avg"].astype(float).round(2).tolist(),
            "rainfall": daily_df["precipitation_sum"].astype(float).round(2).tolist(),
            "precip_probability": daily_df["precipitation_probability_max"].astype(int).tolist(),
            "wind_speed": daily_df["wind_speed_10m_max"].astype(float).round(2).tolist(),
            "wind_gusts": daily_df["wind_gusts_10m_max"].astype(float).round(2).tolist(),
            "et0": daily_df["et0_fao_evapotranspiration"].astype(float).round(2).tolist(),
            "sunshine_duration": (daily_df["sunshine_duration"] / 3600).astype(float).round(2).tolist()
        }

        hourly_df["date_only"] = hourly_df["date"].dt.date
        hourly_grouped = hourly_df.groupby("date_only").agg({
            "temperature_2m": "mean",
            "soil_moisture_0_to_1cm": "mean",
            "soil_moisture_9_to_27cm": "mean",
            "evapotranspiration": "sum",
            "vapor_pressure_deficit": "mean",
            "shortwave_radiation": "mean"
        }).reset_index().fillna(0)

        hourly_series = {
            "dates": hourly_grouped["date_only"].astype(str).tolist(),
            "avg_temp": hourly_grouped["temperature_2m"].astype(float).round(2).tolist(),
            "soil_moisture_surface": hourly_grouped["soil_moisture_0_to_1cm"].astype(float).round(3).tolist(),
            "soil_moisture_root": hourly_grouped["soil_moisture_9_to_27cm"].astype(float).round(3).tolist(),
            "daily_evapotranspiration": hourly_grouped["evapotranspiration"].astype(float).round(2).tolist(),
            "vpd": hourly_grouped["vapor_pressure_deficit"].astype(float).round(2).tolist(),
            "radiation": hourly_grouped["shortwave_radiation"].astype(float).round(2).tolist()
        }

        return {"daily": daily_series, "soil_and_temp": hourly_series}

    def generate_insights(self, daily_df: pd.DataFrame, hourly_df: pd.DataFrame) -> dict:
        daily_df = daily_df.fillna(0)
        hourly_df = hourly_df.fillna(0)
        daily_df['date_only'] = daily_df['date'].dt.date
        hourly_df['date_only'] = hourly_df['date'].dt.date
        
        # Calculate derived columns
        if 'temp_avg' not in daily_df.columns:
            daily_df['temp_avg'] = (daily_df["temperature_2m_max"] + daily_df["temperature_2m_min"]) / 2

        # Core Metrics
        surface_sm = float(hourly_df["soil_moisture_0_to_1cm"].mean())
        root_sm = float(hourly_df["soil_moisture_9_to_27cm"].mean())
        moisture_val = float((surface_sm * 0.4 + root_sm * 0.6) * 100)
        moisture_status = "Good" if 35 < moisture_val < 60 else "Dry" if moisture_val < 20 else "Moderate" if moisture_val < 35 else "Waterlogged"
        
        humidity_mean = float(hourly_df["relative_humidity_2m"].mean())
        humidity_std = float(hourly_df["relative_humidity_2m"].std())
        humidity_status = "STABLE" if humidity_std < 5 else "MODERATE" if humidity_std < 10 else "UNSTABLE"
        
        avg_temp_total = float(daily_df['temp_avg'].mean())
        avg_soil_temp = float(hourly_df['soil_temperature_6cm'].mean())
        harvest_rain = float(daily_df.iloc[-7:]['precipitation_sum'].sum())

        # Decision Blocks
        upcoming_heavy_rain = bool(daily_df.iloc[:3]['precipitation_sum'].max() > 15)
        high_wind = bool(daily_df.iloc[:2]['wind_speed_10m_max'].max() > 20)
        rain_expected = bool(daily_df.iloc[:1]['precipitation_sum'].sum() > 2)
        total_et0_3d = float(daily_df.iloc[:3]['et0_fao_evapotranspiration'].sum())
        days_until_dry = float((moisture_val - 20) / (total_et0_3d / 3)) if total_et0_3d > 0 else 10.0
        insects_risk = bool(avg_temp_total > self.to_u(25) and humidity_mean > 75)

        # Insights Dict
        advanced_insights = {
            "moisture": {"value": round(moisture_val, 1), "unit": "%", "status": moisture_status},
            "air_humidity": {"value": round(humidity_mean, 0), "unit": "%", "status": humidity_status},
            "irrigation_scheduler": {"next_irrigation_days": max(0, int(round(days_until_dry))), "required_water_mm": round(total_et0_3d * 1.2, 1)},
            "fertilizer_advisor": {"status": "Delay" if upcoming_heavy_rain else "Apply", "message": "Delay fertilizer! Rain expected." if upcoming_heavy_rain else "Good window for fertilization."},
            "spray_advisor": {"status": "Do Not Spray" if high_wind or rain_expected else "Safe", "message": "Wind/Rain risk detected." if high_wind or rain_expected else "Safe to spray."},
            "pest_risk": {"status": "High" if insects_risk else "Low", "message": "High insect risk (Warm+Humid)." if insects_risk else "Low pest pressure."},
            "crop_advisory": {
                "germination": "Optimal" if self.to_u(20) < avg_temp_total < self.to_u(30) and moisture_val > 25 else "Risky",
                "flowering": "High Risk" if humidity_mean > 80 else "Good",
                "harvest": "Danger" if harvest_rain > 10 else "Safe"
            },
            "yield_risk": {"score": max(0, 100 - (20 if upcoming_heavy_rain else 0) - (15 if moisture_status == "Dry" else 0)), "rating": "Safe"},
            "dashboard": {
                "action": "Irrigate lightly, avoid spraying tomorrow." if rain_expected else "Good window for farming actions.",
                "yield_risk": "Caution" if upcoming_heavy_rain or moisture_status == "Dry" else "Safe"
            }
        }

        return {
            "advanced_insights": advanced_insights,
            "llm_prompt": f"You are an expert AI Agronomist ({self.unit}). Provide specific actions for irrigation, spraying, and fertilization."
        }

    def get_full_analysis(self, daily_df, hourly_df):
        return {
            "timeseries": self.build_timeseries(daily_df, hourly_df),
            "insights": self.generate_insights(daily_df, hourly_df)
        }