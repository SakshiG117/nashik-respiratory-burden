
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

AIR_FILE = ROOT / "data/processed/combined_air_quality_daily_2019_2025.csv"
WEATHER_FILE = ROOT / "data/processed/weather_daily_2019_2025.csv"
MERGED_FILE = ROOT / "data/processed/air_quality_weather_daily_2019_2025.csv"

air = pd.read_csv(AIR_FILE, parse_dates=["date_local"])
weather = pd.read_csv(WEATHER_FILE, parse_dates=["date_local"])
merged = pd.read_csv(MERGED_FILE, parse_dates=["date_local"])

print("Merged shape:", merged.shape)
print("Duplicate station-date records:",
      merged.duplicated(["station_id", "date_local"]).sum())
print("Missing weather dates:", merged["weather_match"].eq("missing_weather").sum())

missing_dates = sorted(
    set(air["date_local"].dt.date)
    - set(weather["date_local"].dt.date)
)
print("\nFirst 20 dates without weather data:")
print(missing_dates[:20])

print("\nMissing values in weather columns:")
weather_columns = [
    "temperature_mean_c",
    "temperature_min_c",
    "temperature_max_c",
    "precipitation_total_mm",
    "wind_speed_mean_kmh",
    "relative_humidity_mean_pct",
]
print(merged[weather_columns].isna().sum())

assert len(merged) == len(air), "Air-quality rows were lost or duplicated."
assert merged.duplicated(["station_id", "date_local"]).sum() == 0
assert merged["weather_match"].notna().all()

print("\nMerged dataset validation passed.")