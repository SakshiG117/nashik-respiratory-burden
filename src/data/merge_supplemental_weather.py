
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

EXISTING_FILE = ROOT / "data/processed/weather_daily_2019_2025.csv"
RAW_FILE = ROOT / "data/raw/weather_api_hourly_2025-12-07_2025-12-31.csv"
OUTPUT_FILE = ROOT / "data/processed/weather_daily_2019_2025.csv"

# Load the existing daily dataset and supplemental hourly data.
existing = pd.read_csv(EXISTING_FILE, parse_dates=["date_local"])
hourly = pd.read_csv(RAW_FILE, parse_dates=["timestamp"])

# Aggregate the API data using the same daily definitions.
hourly["date_local"] = hourly["timestamp"].dt.normalize()

daily = (
    hourly.groupby("date_local")
    .agg(
        temperature_mean_c=("temperature_c", "mean"),
        temperature_min_c=("temperature_c", "min"),
        temperature_max_c=("temperature_c", "max"),
        precipitation_total_mm=("precipitation_mm", "sum"),
        wind_speed_mean_kmh=("wind_speed_kmh", "mean"),
        relative_humidity_mean_pct=("relative_humidity_pct", "mean"),
        hourly_records=("timestamp", "count"),
    )
    .reset_index()
)

daily["coverage_flag"] = daily["hourly_records"].apply(
    lambda n: "complete_24_hours" if n == 24 else "incomplete_day"
)

# Add provenance so we know where each day's weather came from.
if "weather_source" not in existing.columns:
    existing["weather_source"] = "Original weather CSV"

daily["weather_source"] = "Open-Meteo Historical Weather API"

# Check the supplement covers exactly December 7–31, 2025.
expected_dates = pd.date_range("2025-12-07", "2025-12-31")
actual_dates = pd.DatetimeIndex(daily["date_local"])

if not actual_dates.equals(expected_dates):
    raise ValueError(
        "Supplemental dates are incomplete or unexpected. "
        f"Received {len(actual_dates)} dates."
    )

# Do not allow the supplemental data to overwrite existing dates.
overlap = set(existing["date_local"]) & set(daily["date_local"])
if overlap:
    raise ValueError(f"Dates already exist in the daily dataset: {overlap}")

combined = pd.concat([existing, daily], ignore_index=True)
combined = combined.sort_values("date_local").reset_index(drop=True)

if combined["date_local"].duplicated().any():
    raise ValueError("Duplicate dates found after combining weather data.")

combined.to_csv(OUTPUT_FILE, index=False)

print("Weather datasets combined successfully.")
print("Existing daily rows:", len(existing))
print("New daily rows:", len(daily))
print("Combined daily rows:", len(combined))
print("New records with 24 hours:", (daily["hourly_records"] == 24).sum())
print("Date range:", combined["date_local"].min(), "to", combined["date_local"].max())
print("Weather source counts:")
print(combined["weather_source"].value_counts())
print("Saved to:", OUTPUT_FILE)