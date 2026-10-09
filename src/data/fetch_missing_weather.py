
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/raw/weather_api_hourly_2025-12-07_2025-12-31.csv"
)

URL = "https://archive-api.open-meteo.com/v1/archive"

params = {
    "latitude": 19.999998,
    "longitude": 73.8,
    "start_date": "2025-12-07",
    "end_date": "2025-12-31",
    "hourly": (
        "temperature_2m,precipitation,"
        "wind_speed_10m,relative_humidity_2m"
    ),
    "timezone": "Asia/Kolkata",
    "temperature_unit": "celsius",
    "wind_speed_unit": "kmh",
    "precipitation_unit": "mm",
}

print("Requesting missing historical weather data...")

response = requests.get(URL, params=params, timeout=60)
response.raise_for_status()
data = response.json()

if "hourly" not in data:
    raise ValueError(f"Hourly data missing from API response: {data}")

hourly = pd.DataFrame(data["hourly"])

hourly = hourly.rename(columns={
    "time": "timestamp",
    "temperature_2m": "temperature_c",
    "precipitation": "precipitation_mm",
    "wind_speed_10m": "wind_speed_kmh",
    "relative_humidity_2m": "relative_humidity_pct",
})

hourly["timestamp"] = pd.to_datetime(
    hourly["timestamp"], errors="coerce"
)

if hourly["timestamp"].isna().any():
    raise ValueError("Invalid timestamps returned by the API.")

if hourly["timestamp"].duplicated().any():
    raise ValueError("Duplicate timestamps returned by the API.")

hourly["weather_source"] = "Open-Meteo Historical Weather API"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
hourly.to_csv(OUTPUT_FILE, index=False)

print("\nDownload completed.")
print("Hourly records:", len(hourly))
print("First timestamp:", hourly["timestamp"].min())
print("Last timestamp:", hourly["timestamp"].max())
print("Missing values:\n", hourly.isna().sum())
print("Saved to:", OUTPUT_FILE)