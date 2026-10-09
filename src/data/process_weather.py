
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data/raw/weather_hourly_2019_2025.csv"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/weather_daily_2019_2025.csv"

# Read the combined CSV; the first three lines contain metadata/spacing.
df = pd.read_csv(INPUT_FILE, skiprows=3)

# Keep only hourly records. The daily section has date-only timestamps.
df = df[df["time"].astype(str).str.contains("T", regex=False)].copy()

df = df.rename(columns={
    "time": "timestamp",
    "temperature_2m (°C)": "temperature_c",
    "precipitation (mm)": "precipitation_mm",
    "wind_speed_10m (km/h)": "wind_speed_kmh",
    "relative_humidity_2m (%)": "relative_humidity_pct",
})

# Interpret source timestamps as UTC and convert to Indian Standard Time.
df["timestamp"] = pd.to_datetime(
    df["timestamp"], errors="coerce", utc=True
)
df = df.dropna(subset=["timestamp"])
df["timestamp"] = df["timestamp"].dt.tz_convert("Asia/Kolkata")

value_columns = [
    "temperature_c",
    "precipitation_mm",
    "wind_speed_kmh",
    "relative_humidity_pct",
]

for column in value_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df = df.sort_values("timestamp").drop_duplicates(subset=["timestamp"])

# Calculate daily summaries using local Indian dates.
df["date_local"] = df["timestamp"].dt.strftime("%Y-%m-%d")

daily = df.groupby("date_local", as_index=False).agg(
    temperature_mean_c=("temperature_c", "mean"),
    temperature_min_c=("temperature_c", "min"),
    temperature_max_c=("temperature_c", "max"),
    precipitation_total_mm=("precipitation_mm", "sum"),
    wind_speed_mean_kmh=("wind_speed_kmh", "mean"),
    relative_humidity_mean_pct=("relative_humidity_pct", "mean"),
    hourly_records=("timestamp", "count"),
)

# Flag incomplete days rather than inventing missing hourly observations.
daily["coverage_flag"] = daily["hourly_records"].apply(
    lambda n: "complete_24_hours" if n == 24 else "incomplete_day"
)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
daily.to_csv(OUTPUT_FILE, index=False)

print("Weather processing completed.")
print("Hourly rows used:", len(df))
print("Daily rows created:", len(daily))
print("Date range:", daily["date_local"].min(), "to", daily["date_local"].max())
print("Incomplete days:", (daily["hourly_records"] < 24).sum())
print("Missing values:\n", daily.isna().sum())
print("\nCoverage flags:\n", daily["coverage_flag"].value_counts())
print("\nLast five daily records:\n", daily.tail().to_string(index=False))