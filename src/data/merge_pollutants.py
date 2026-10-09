
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PM25_FILE = PROCESSED_DIR / "pm25_daily_2019_2025.csv"
OTHER_FILE = PROCESSED_DIR / "other_pollutants_daily_2019_2025.csv"
OUTPUT_FILE = PROCESSED_DIR / "combined_air_quality_daily_2019_2025.csv"

# Load processed datasets
pm25 = pd.read_csv(PM25_FILE)
other = pd.read_csv(OTHER_FILE)

# Standardize station names and dates
for df in (pm25, other):
    df["station_name"] = (
        df["station_name"].astype(str).str.strip()
    )
    df["date_local"] = pd.to_datetime(
        df["date_local"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

other["station_name"] = other["station_name"].replace({
    "MIDCAmbad": "MIDC Ambad"
})

# Preserve each pollutant's original unit in separate columns.
# Do not mix ppb and µg/m³ measurements in the same column.
other_pivot = other.pivot(
    index=["station_id", "station_name", "date_local"],
    columns=["parameter", "unit"],
    values="value",
)

other_pivot.columns = [
    f"{parameter}_{unit.replace('µg/m³', 'ug_m3').replace('/', '_').replace(' ', '')}"
    for parameter, unit in other_pivot.columns
]
other_pivot = other_pivot.reset_index()

# Keep PM2.5 and its source unit
pm25 = pm25[
    [
        "station_id", "station_name", "date_local",
        "value", "unit", "latitude", "longitude"
    ]
].rename(columns={
    "value": "pm25_value",
    "unit": "pm25_unit",
})

# Merge on station identity and date
combined = pm25.merge(
    other_pivot,
    on=["station_id", "station_name", "date_local"],
    how="left",
    validate="one_to_one",
)

# Add coordinates if they were not retained from PM2.5
if "latitude" not in combined.columns:
    combined["latitude"] = combined["station_name"].map({
        "Gangapur Road": 20.0073285,
        "Pandav Nagari": 19.9591346,
        "MIDC Ambad": 19.95022,
        "Hirawadi": 20.021503,
    })

if "longitude" not in combined.columns:
    combined["longitude"] = combined["station_name"].map({
        "Gangapur Road": 73.7762427,
        "Pandav Nagari": 73.7788008,
        "MIDC Ambad": 73.73148,
        "Hirawadi": 73.813844,
    })

# Sort and save
combined = combined.sort_values(
    ["station_name", "date_local"]
).reset_index(drop=True)

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
combined.to_csv(OUTPUT_FILE, index=False)

print("Combined dataset created.")
print(f"File: {OUTPUT_FILE}")
print(f"Rows: {len(combined)}")
print(f"Columns: {len(combined.columns)}")

print("\nColumn names:")
print(combined.columns.tolist())

print("\nMissing values by column:")
print(combined.isna().sum().to_string())

print("\nPreview:")
print(combined.head().to_string(index=False))