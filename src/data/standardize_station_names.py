
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "other_pollutants_daily_2019_2025.csv"
)

df = pd.read_csv(FILE)

print("Station names before correction:")
print(sorted(df["station_name"].dropna().unique()))

# Standardize whitespace and known station-name variation.
df["station_name"] = (
    df["station_name"]
    .astype(str)
    .str.strip()
    .replace({
        "MIDCAmbad": "MIDC Ambad",
        "MIDC Ambad": "MIDC Ambad",
    })
)

df.to_csv(FILE, index=False)

print("\nStation names after correction:")
print(sorted(df["station_name"].dropna().unique()))

print("\nUpdated processed file:")
print(FILE)