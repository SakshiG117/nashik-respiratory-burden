
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FILE = PROJECT_ROOT / "data/processed/weather_daily_2019_2025.csv"

df = pd.read_csv(FILE)

print("Dataset shape:", df.shape)
print("Date range:", df["date_local"].min(), "to", df["date_local"].max())
print("Duplicate dates:", df["date_local"].duplicated().sum())
print("Missing values:\n", df.isna().sum())
print("Hourly record counts:\n", df["hourly_records"].value_counts().sort_index())
print("Incomplete days:\n", df[df["coverage_flag"] != "complete_24_hours"].to_string(index=False))

assert df["date_local"].is_unique, "Duplicate dates found."
assert df["date_local"].notna().all(), "Missing dates found."
assert df["hourly_records"].between(1, 24).all(), "Unexpected hourly count."
assert (df["hourly_records"] == 24).sum() == 2530, "Unexpected complete-day count."

print("\nWeather validation passed.")