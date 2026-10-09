
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

print("\n1. Records with missing pollutant values")
print(
    df[df["value"].isna()].to_string(index=False)
)

print("\n2. Records with negative values")
print(
    df[df["value"] < 0].to_string(index=False)
)

print("\n3. Records with mixed units")
mixed_parameters = (
    df.groupby("parameter")["unit"]
    .nunique()
)

mixed_names = mixed_parameters[
    mixed_parameters > 1
].index

print(
    df[df["parameter"].isin(mixed_names)]
    .groupby(["parameter", "unit"])
    .agg(
        records=("value", "size"),
        missing_values=("value", lambda x: x.isna().sum()),
        minimum=("value", "min"),
        median=("value", "median"),
        maximum=("value", "max"),
    )
    .round(3)
    .to_string()
)

print("\n4. Highest CO readings")
print(
    df[df["parameter"] == "co"]
    .nlargest(10, "value")[
        [
            "station_name",
            "sensor_id",
            "date_local",
            "value",
            "unit",
        ]
    ]
    .to_string(index=False)
)