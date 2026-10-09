
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw"
    / "openaq_other_pollutants_daily_2019_2025.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed"
    / "other_pollutants_daily_2019_2025.csv"
)

df = pd.read_csv(INPUT_FILE)

# 1. Standardize column formats
df["date_local"] = pd.to_datetime(
    df["date_local"], errors="coerce"
)
df["parameter"] = (
    df["parameter"].astype(str).str.lower().str.strip()
)
df["unit"] = df["unit"].astype(str).str.strip()
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# 2. Keep only the required date range
df = df[
    (df["date_local"] >= "2019-01-01")
    & (df["date_local"] < "2026-01-01")
].copy()

# 3. Add transparent quality flags
df["quality_flag"] = "check_required"

df.loc[df["value"].isna(), "quality_flag"] = "missing_value"

df.loc[
    df["value"] < 0, "quality_flag"
] = "negative_value_review"

# Flag unusually high values for investigation, not automatic removal.
high_value_limits = {
    "co": 10000,
    "no2": 500,
    "o3": 200,
    "pm10": 500,
    "so2": 200,
}

for parameter, limit in high_value_limits.items():
    mask = (
        (df["parameter"] == parameter)
        & (df["value"] > limit)
        & (df["quality_flag"] == "check_required")
    )
    df.loc[mask, "quality_flag"] = "high_value_review"

# 4. Keep original values and units.
# Do not convert mixed units until conversion rules are documented.

# 5. Sort and save
df = df.sort_values(
    ["parameter", "station_name", "date_local"]
).reset_index(drop=True)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_FILE, index=False)

print("Processing completed.")
print(f"Output file: {OUTPUT_FILE}")
print(f"Total records: {len(df)}")

print("\nQuality flags:")
print(df["quality_flag"].value_counts().to_string())

print("\nUnits by pollutant:")
print(
    df.groupby("parameter")["unit"]
    .unique()
    .to_string()
)