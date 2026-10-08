import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv


# ============================================================
# 1. LOAD API KEY
# ============================================================

load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env file")

headers = {
    "X-API-Key": api_key
}


# ============================================================
# 2. PM2.5 SENSORS IN NASHIK
# ============================================================

sensors = {
    14794: {
        "station_id": 5592,
        "station_name": "Gangapur Road",
        "latitude": 20.0073285,
        "longitude": 73.7762427
    },

    12235635: {
        "station_id": 5592,
        "station_name": "Gangapur Road",
        "latitude": 20.0073285,
        "longitude": 73.7762427
    },

    12238112: {
        "station_id": 3409451,
        "station_name": "Pandav Nagari",
        "latitude": 19.9591346,
        "longitude": 73.7788008
    },

    12238130: {
        "station_id": 3409453,
        "station_name": "MIDC Ambad",
        "latitude": 19.95022,
        "longitude": 73.73148
    },

    12238139: {
        "station_id": 3409454,
        "station_name": "Hirawadi",
        "latitude": 20.021503,
        "longitude": 73.813844
    }
}


# ============================================================
# 3. DATE RANGE
# ============================================================

date_from = "2019-01-01T00:00:00+05:30"
date_to = "2025-12-31T23:59:59+05:30"


# ============================================================
# 4. DOWNLOAD DATA
# ============================================================

all_data = []

for sensor_id, station_info in sensors.items():

    station_name = station_info["station_name"]
    station_id = station_info["station_id"]

    print("\n" + "=" * 70)
    print("Downloading PM2.5")
    print(f"Station : {station_name}")
    print(f"Sensor  : {sensor_id}")
    print("=" * 70)

    page = 1

    while True:

        url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days"

        params = {
            "datetime_from": date_from,
            "datetime_to": date_to,
            "limit": 1000,
            "page": page
        }

        response = requests.get(
            url,
            headers=headers,
            params=params
        )

        print(
            f"Page {page} | "
            f"Status code: {response.status_code}"
        )

        if response.status_code != 200:
            print("API request failed.")
            print(response.text)
            break

        data = response.json()

        results = data.get("results", [])

        if not results:
            break

        for record in results:

            period = record.get("period") or {}
            datetime_from = period.get("datetimeFrom") or {}

            parameter = record.get("parameter") or {}

            all_data.append({
                "station_id": station_id,
                "station_name": station_name,
                "sensor_id": sensor_id,
                "parameter": parameter.get("name"),
                "unit": parameter.get("units"),
                "date_local": datetime_from.get("local"),
                "value": record.get("value"),
                "latitude": station_info["latitude"],
                "longitude": station_info["longitude"]
            })

        print(f"Records received: {len(results)}")

        if len(results) < 1000:
            break

        page += 1

        time.sleep(0.2)


# ============================================================
# 5. CREATE DATAFRAME
# ============================================================

df = pd.DataFrame(all_data)


# ============================================================
# 6. SAVE RAW DOWNLOADED DATA
# ============================================================

output_file = "data/raw/openaq_pm25_daily_2019_2025.csv"

df.to_csv(
    output_file,
    index=False
)


# ============================================================
# 7. BASIC SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("DOWNLOAD COMPLETED")
print("=" * 70)

print(f"Total records: {len(df)}")
print(f"Saved to: {output_file}")

print("\nRecords by station:")

if not df.empty:
    print(
        df.groupby("station_name")
        .size()
        .to_string()
    )

print("\nDate range by station:")

if not df.empty:
    print(
        df.groupby("station_name")["date_local"]
        .agg(["min", "max"])
        .to_string()
    )

print("\nMissing PM2.5 values:")

if not df.empty:
    print(df["value"].isna().sum())

print("\nFirst 10 records:")

if not df.empty:
    print(
        df.head(10)
        .to_string(index=False)
    )