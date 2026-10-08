import os
import requests
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Get API key
api_key = os.getenv("OPENAQ_API_KEY")

if not api_key:
    raise ValueError("OPENAQ_API_KEY not found in .env file")

# Gangapur Road, Nashik - MPCB
location_id = 5592

url = f"https://api.openaq.org/v3/locations/{location_id}"

headers = {
    "X-API-Key": api_key
}

response = requests.get(url, headers=headers)

print("Status code:", response.status_code)

if response.status_code == 200:
    data = response.json()

    location = data["results"][0]

    print("\nConnection successful!")
    print("Location:", location["name"])
    print("Location ID:", location["id"])
    print("Country:", location["country"]["name"])
    print("Timezone:", location["timezone"])

else:
    print("\nAPI request failed.")
    print(response.text)