import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env file")

headers = {
    "X-API-Key": api_key
}

# All four Nashik MPCB monitoring stations
stations = {
    5592: "Gangapur Road",
    3409451: "Pandav Nagari",
    3409453: "MIDC Ambad",
    3409454: "Hirawadi"
}

rows = []

for location_id, station_name in stations.items():

    print(f"\nChecking station: {station_name}")

    # First get the station information
    location_url = f"https://api.openaq.org/v3/locations/{location_id}"

    response = requests.get(
        location_url,
        headers=headers
    )

    if response.status_code != 200:
        print(
            f"Failed to get {station_name}: "
            f"{response.status_code}"
        )
        continue

    location = response.json()["results"][0]

    # Get each sensor's detailed information
    for sensor in location.get("sensors", []):

        sensor_id = sensor.get("id")

        sensor_url = (
            f"https://api.openaq.org/v3/sensors/{sensor_id}"
        )

        sensor_response = requests.get(
            sensor_url,
            headers=headers
        )

        if sensor_response.status_code != 200:
            print(
                f"  Failed sensor {sensor_id}: "
                f"{sensor_response.status_code}"
            )
            continue

        sensor_data = sensor_response.json()["results"][0]

        parameter = sensor_data.get("parameter", {})
        coverage = sensor_data.get("coverage") or {}

        datetime_first = sensor_data.get("datetimeFirst") or {}
        datetime_last = sensor_data.get("datetimeLast") or {}

        rows.append({
            "station_id": location_id,
            "station_name": station_name,
            "sensor_id": sensor_id,
            "parameter": parameter.get("name"),
            "unit": parameter.get("units"),

            "first_date_utc": datetime_first.get("utc"),
            "first_date_local": datetime_first.get("local"),

            "last_date_utc": datetime_last.get("utc"),
            "last_date_local": datetime_last.get("local"),

            "percent_coverage": coverage.get("percentCoverage"),
            "percent_complete": coverage.get("percentComplete"),

            "observed_count": coverage.get("observedCount"),
            "expected_count": coverage.get("expectedCount")
        })

        print(
            f"  Sensor {sensor_id}: "
            f"{parameter.get('name')} | "
            f"{datetime_first.get('local')} → "
            f"{datetime_last.get('local')}"
        )


# Create DataFrame
df = pd.DataFrame(rows)

# Sort
df = df.sort_values(
    ["station_name", "parameter", "sensor_id"]
)

# Save report
output_file = "data/processed/openaq_sensor_availability.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n" + "=" * 80)
print("Sensor availability report created.")
print(f"Total sensors checked: {len(df)}")
print(f"Saved to: {output_file}")
print("=" * 80)

print("\nSummary:\n")

print(
    df[
        [
            "station_name",
            "sensor_id",
            "parameter",
            "unit",
            "first_date_local",
            "last_date_local",
            "percent_coverage"
        ]
    ].to_string(index=False)
)