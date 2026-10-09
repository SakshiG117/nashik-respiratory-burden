
import pandas as pd

file_path = "data/raw/openaq_other_pollutants_daily_2019_2025.csv"

df = pd.read_csv(file_path)
df["date_local"] = pd.to_datetime(df["date_local"])

targets = [
    ("co", 14868, "2022-03-25"),
    ("no2", 14798, "2019-10-22"),
    ("so2", 14793, "2021-06-28"),
]

columns = [
    "date_local",
    "station_name",
    "sensor_id",
    "parameter",
    "unit",
    "value",
]

for parameter, sensor_id, target_date in targets:
    target = pd.Timestamp(target_date)

    nearby = df[
        (df["parameter"] == parameter)
        & (df["sensor_id"] == sensor_id)
        & (
            (df["date_local"] >= target - pd.Timedelta(days=3))
            & (df["date_local"] <= target + pd.Timedelta(days=3))
        )
    ].sort_values("date_local")

    print(f"\n--- {parameter.upper()} | Sensor {sensor_id} | {target_date} ---")

    if nearby.empty:
        print("No nearby records found.")
    else:
        print(nearby[columns].to_string(index=False))