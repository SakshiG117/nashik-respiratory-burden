
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

AIR_FILE = (
    PROJECT_ROOT
    / "data/processed/combined_air_quality_daily_2019_2025.csv"
)
WEATHER_FILE = (
    PROJECT_ROOT
    / "data/processed/weather_daily_2019_2025.csv"
)
OUTPUT_FILE = (
    PROJECT_ROOT
    / "data/processed/air_quality_weather_daily_2019_2025.csv"
)

air = pd.read_csv(AIR_FILE, parse_dates=["date_local"])
weather = pd.read_csv(WEATHER_FILE, parse_dates=["date_local"])

# Verify the weather data has only one record per date.
if weather["date_local"].duplicated().any():
    raise ValueError("Duplicate dates found in the weather dataset.")

# Retain all air-quality records, even when weather data is unavailable.
merged = air.merge(
    weather,
    on="date_local",
    how="left",
    validate="many_to_one",
    indicator=True,
)

merged["weather_match"] = merged["_merge"].map({
    "both": "available",
    "left_only": "missing_weather",
})
merged = merged.drop(columns="_merge")

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
merged.to_csv(OUTPUT_FILE, index=False)

print("Merge completed.")
print("Air-quality rows:", len(air))
print("Merged rows:", len(merged))
print("Monitoring stations:", merged["station_name"].nunique())
print("Date range:", merged["date_local"].min(), "to", merged["date_local"].max())
print("\nWeather availability:")
print(merged["weather_match"].value_counts())
print("\nWeather coverage flags:")
print(merged["coverage_flag"].value_counts(dropna=False))
print("\nOutput:", OUTPUT_FILE)