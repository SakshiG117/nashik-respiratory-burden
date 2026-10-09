
import os
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# 1. PROJECT SETTINGS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAQ_API_KEY not found in the project .env file."
    )

headers = {"X-API-Key": api_key}

availability_file = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "openaq_sensor_availability.csv"
)

output_file = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq_other_pollutants_daily_2019_2025.csv"
)

date_from = "2019-01-01T00:00:00+05:30"
date_to = "2025-12-31T23:59:59+05:30"

target_parameters = ["pm10", "no2", "so2", "co", "o3"]


# Station coordinates from the existing project configuration.
station_coordinates = {
    "Gangapur Road": (20.0073285, 73.7762427),
    "Pandav Nagari": (19.9591346, 73.7788008),
    "MIDC Ambad": (19.95022, 73.73148),
    "Hirawadi": (20.021503, 73.813844),
}


# --------------------------------------------------
# 2. LOAD AND SELECT SENSORS
# --------------------------------------------------

availability = pd.read_csv(availability_file)

availability["parameter"] = (
    availability["parameter"]
    .astype(str)
    .str.lower()
    .str.strip()
)

sensors = availability[
    availability["parameter"].isin(target_parameters)
].copy()

sensors = sensors.drop_duplicates(subset=["sensor_id"])

print("Sensors selected by pollutant:")
print(
    sensors.groupby("parameter")["sensor_id"]
    .count()
    .to_string()
)


# --------------------------------------------------
# 3. DOWNLOAD DAILY SENSOR DATA
# --------------------------------------------------

all_data = []
failed_sensors = []

for _, sensor in sensors.iterrows():

    sensor_id = int(sensor["sensor_id"])
    parameter_name = sensor["parameter"]
    station_name = sensor["station_name"]

    latitude, longitude = station_coordinates.get(
        station_name, (None, None)
    )

    print(
        f"\nDownloading {parameter_name.upper()} | "
        f"{station_name} | Sensor {sensor_id}"
    )

    url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days"
    page = 1

    while True:

        params = {
            "datetime_from": date_from,
            "datetime_to": date_to,
            "limit": 1000,
            "page": page,
        }

        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )

        except requests.RequestException as exc:
            print(f"Network error: {exc}")

            failed_sensors.append({
                "sensor_id": sensor_id,
                "station_name": station_name,
                "parameter": parameter_name,
                "reason": str(exc),
            })
            break

        print(f"Page {page} | HTTP {response.status_code}")

        if response.status_code != 200:
            print(f"Request failed: {response.text[:300]}")

            failed_sensors.append({
                "sensor_id": sensor_id,
                "station_name": station_name,
                "parameter": parameter_name,
                "reason": f"HTTP {response.status_code}",
            })
            break

        results = response.json().get("results", [])

        if not results:
            break

        for record in results:

            period = record.get("period") or {}
            datetime_from = period.get("datetimeFrom") or {}
            record_parameter = record.get("parameter") or {}

            all_data.append({
                "station_id": sensor["station_id"],
                "station_name": station_name,
                "sensor_id": sensor_id,
                "parameter": parameter_name,
                "unit": record_parameter.get("units"),
                "date_local": datetime_from.get("local"),
                "value": record.get("value"),
                "latitude": latitude,
                "longitude": longitude,
            })

        if len(results) < 1000:
            break

        page += 1
        time.sleep(0.2)


# --------------------------------------------------
# 4. CREATE AND CLEAN DATAFRAME
# --------------------------------------------------

columns = [
    "station_id",
    "station_name",
    "sensor_id",
    "parameter",
    "unit",
    "date_local",
    "value",
    "latitude",
    "longitude",
]

df = pd.DataFrame(all_data, columns=columns)

if not df.empty:

    # Extract the local calendar date before parsing.
    # This avoids timezone-aware versus timezone-naive errors.
    df["date_local"] = pd.to_datetime(
        df["date_local"].astype(str).str[:10],
        errors="coerce",
    )

    # Remove invalid dates.
    df = df.dropna(subset=["date_local"]).copy()

    # Keep only records from 2019 through 2025.
    df = df[
        (df["date_local"] >= pd.Timestamp("2019-01-01"))
        & (df["date_local"] < pd.Timestamp("2026-01-01"))
    ].copy()

    # Remove exact duplicate sensor-date records.
    df = df.drop_duplicates(
        subset=["sensor_id", "date_local"]
    )

    # Sort records for easier inspection.
    df = df.sort_values(
        ["parameter", "station_name", "date_local"]
    )

    # Save dates in YYYY-MM-DD format.
    df["date_local"] = df["date_local"].dt.strftime(
        "%Y-%m-%d"
    )

    # Keep the raw download separate from processed data.
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(output_file, index=False)

else:
    print("\nNo records were downloaded.")
    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


# --------------------------------------------------
# 5. DOWNLOAD SUMMARY
# --------------------------------------------------

print("\n" + "=" * 55)
print("DOWNLOAD SUMMARY")
print("=" * 55)

print(f"Total records: {len(df):,}")
print(f"Output file: {output_file}")

if not df.empty:

    print("\nRecords by pollutant:")
    print(df.groupby("parameter").size().to_string())

    print("\nRecords by station and pollutant:")
    print(
        df.groupby(["station_name", "parameter"])
        .size()
        .to_string()
    )

    print("\nDate range by pollutant:")
    date_summary = df.copy()
    date_summary["date_local"] = pd.to_datetime(
        date_summary["date_local"]
    )

    print(
        date_summary.groupby("parameter")["date_local"]
        .agg(["min", "max", "count"])
        .to_string()
    )

    print("\nMissing values by column:")
    print(df.isna().sum().to_string())

print(f"\nFailed sensor requests: {len(failed_sensors)}")

if failed_sensors:
    print("\nFailed requests:")
    for failure in failed_sensors:
        print(failure)

print("\nDownload script finished.")