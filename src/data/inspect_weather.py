from pathlib import Path
import pandas as pd

project_root = Path(__file__).resolve().parents[2]
file_path = project_root / "data/raw/weather_hourly_2019_2025.csv"

df = pd.read_csv(file_path, skiprows=3)

timestamps = df["time"].astype(str)

print("Total rows:", len(df))
print("Rows with hourly timestamps:", timestamps.str.contains("T", regex=False).sum())
print("Rows with date-only timestamps:", (~timestamps.str.contains("T", regex=False)).sum())

print("\nFirst date-only rows:")
print(df.loc[~timestamps.str.contains("T", regex=False)].head(5).to_string(index=False))

print("\nLast 10 source rows:")
print(df.tail(10).to_string(index=False))