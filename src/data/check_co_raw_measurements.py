
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env")

sensor_id = 12235630
url = f"https://api.openaq.org/v3/sensors/{sensor_id}/measurements"

params = {
    "datetime_from": "2025-03-01T00:00:00+05:30",
    "datetime_to": "2025-03-04T00:00:00+05:30",
    "limit": 1000,
    "page": 1,
}

response = requests.get(
    url,
    headers={"X-API-Key": api_key},
    params=params,
    timeout=30,
)
response.raise_for_status()

data = response.json()
records = data.get("results", [])

print("Original measurements returned:", len(records))

for record in records[:15]:
    period = record.get("period") or {}
    print({
        "value": record.get("value"),
        "unit": (record.get("parameter") or {}).get("units"),
        "period": period,
        "flags": record.get("flagInfo"),
    })