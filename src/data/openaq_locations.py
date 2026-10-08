import os
import requests
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()

api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env file")

# Nashik city approximate centre
latitude = 20.0059
longitude = 73.7797

# Search within 25 km of Nashik
radius = 25000

url = "https://api.openaq.org/v3/locations"

params = {
    "coordinates": f"{latitude},{longitude}",
    "radius": radius,
    "limit": 100
}

headers = {
    "X-API-Key": api_key
}

response = requests.get(
    url,
    params=params,
    headers=headers
)

print("Status code:", response.status_code)

if response.status_code != 200:
    print("API request failed:")
    print(response.text)
    raise SystemExit

data = response.json()

locations = data["results"]

print(f"\nLocations found: {len(locations)}")
print("=" * 80)

for location in locations:

    print(f"\nLocation ID : {location['id']}")
    print(f"Name        : {location['name']}")
    print(f"Locality    : {location.get('locality')}")
    print(f"Monitor     : {location.get('isMonitor')}")
    print(f"Mobile      : {location.get('isMobile')}")

    coordinates = location.get("coordinates", {})

    print(
        f"Coordinates : "
        f"{coordinates.get('latitude')}, "
        f"{coordinates.get('longitude')}"
    )

    print(
        f"Owner       : "
        f"{location.get('owner', {}).get('name')}"
    )

    print(
        f"Provider    : "
        f"{location.get('provider', {}).get('name')}"
    )

    print("Sensors     :")

    for sensor in location.get("sensors", []):
        parameter = sensor.get("parameter", {})

        print(
            f"   - Sensor {sensor.get('id')}: "
            f"{parameter.get('name')} "
            f"({parameter.get('units')})"
        )

print("\n" + "=" * 80)
print("Station discovery completed.")