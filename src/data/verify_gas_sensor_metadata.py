
import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError(
        "OPENAQ_API_KEY not found. Check the variable name in your .env file."
    )

sensor_ids = [
    14868,       # Older Gangapur Road CO
    12235630,    # Newer Gangapur Road CO
    12238134,    # Hirawadi CO
    12238125,    # MIDC Ambad CO
    12241407,    # Pandav Nagari CO
    14798,       # Older Gangapur Road NO2
    14793,       # Older Gangapur Road SO2
]

headers = {"X-API-Key": api_key}

for sensor_id in sensor_ids:
    url = f"https://api.openaq.org/v3/sensors/{sensor_id}"

    try:
        response = requests.get(
            url, headers=headers, timeout=20
        )
        response.raise_for_status()
        payload = response.json()

        results = payload.get("results", [])
        if not results:
            print(f"\nSensor {sensor_id}: no metadata returned")
            continue

        sensor = results[0]
        parameter = sensor.get("parameter") or {}

        print(f"\nSensor ID: {sensor_id}")
        print("Name:", sensor.get("name"))
        print("Parameter:", parameter.get("name"))
        print("Reported unit:", parameter.get("units"))
        print("Display name:", parameter.get("displayName"))

    except requests.RequestException as error:
        print(f"\nSensor {sensor_id}: request failed ({error})")