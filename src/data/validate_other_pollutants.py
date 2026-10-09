
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

input_file = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq_other_pollutants_daily_2019_2025.csv"
)

df = pd.read_csv(input_file)

print("=" * 55)
print("OTHER POLLUTANTS DATA VALIDATION")
print("=" * 55)

print("\nDataset shape:")
print(df.shape)

print("\nData types:")
print(df.dtypes)

print("\nMissing values:")
print(df.isna().sum())

print("\nDuplicate sensor-date records:")
print(
    df.duplicated(
        subset=["sensor_id", "date_local"]
    ).sum()
)

print("\nRecords outside 2019-2025:")
dates = pd.to_datetime(df["date_local"], errors="coerce")

print(
    (
        (dates < "2019-01-01")
        | (dates >= "2026-01-01")
        | dates.isna()
    ).sum()
)

print("\nNegative pollutant values:")
print((df["value"] < 0).sum())

print("\nRecords by pollutant:")
print(df.groupby("parameter").size().to_string())

print("\nValue statistics by pollutant:")
print(
    df.groupby("parameter")["value"]
    .agg(["count", "mean", "median", "min", "max"])
    .round(3)
    .to_string()
)

print("\nRecords by year and pollutant:")
df["year"] = dates.dt.year
print(
    df.groupby(["year", "parameter"])
    .size()
    .unstack(fill_value=0)
    .to_string()
)

print("\nUnits by pollutant:")
print(
    df.groupby("parameter")["unit"]
    .unique()
    .to_string()
)

print("\nValidation inspection completed.")