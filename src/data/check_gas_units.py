
import pandas as pd

input_path = "data/processed/other_pollutants_quality_audit.csv"
df = pd.read_csv(input_path)

gas_parameters = ["co", "no2", "so2"]

gas = df[df["parameter"].isin(gas_parameters)]

summary = (
    gas.groupby(["station_name", "sensor_id", "parameter", "unit"])
    .agg(
        records=("value", "count"),
        first_date=("date_local", "min"),
        last_date=("date_local", "max"),
        median_value=("value", "median"),
        max_value=("value", "max"),
    )
    .reset_index()
    .sort_values(["parameter", "station_name", "first_date"])
)

print("GAS SENSOR UNIT SUMMARY")
print(summary.to_string(index=False))

print("\nUNIT COUNTS BY POLLUTANT")
print(
    gas.groupby(["parameter", "unit"])
    .size()
    .unstack(fill_value=0)
    .to_string()
)