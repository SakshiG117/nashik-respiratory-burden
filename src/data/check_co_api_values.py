
import os
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env")

sensor_id = 12235630
url = f"https://api.openaq.org/v3/sensors/{sensor_id}/days"

params = {
    "date_from": "2025-03-01T00:00:00Z",
    "date_to": "2025-03-08T00:00:00Z",
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

payload = response.json()
results = payload.get("results", [])

print("API records returned:", len(results))

if results:
    print("\nFirst API record:")
    print(results[0])

    print("\nDate and value summary:")
    records = pd.json_normalize(results)
    print(records.to_string(index=False))
else:
    print("No records returned for this date range.")