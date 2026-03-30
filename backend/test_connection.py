import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Print loaded variables (masked for security)
token_key = os.getenv("STREAMLINE_TOKEN_KEY")
token_secret = os.getenv("STREAMLINE_SECRET_KEY")
base_url = os.getenv("STREAMLINE_BASE_URL")

print("=== ENV CHECK ===")
print(f"STREAMLINE_BASE_URL: {base_url}")
print(f"STREAMLINE_TOKEN_KEY loaded: {'Yes' if token_key else 'No'}")
print(f"STREAMLINE_TOKEN_SECRET loaded: {'Yes' if token_secret else 'No'}")
print("=================\n")

payload = {
    "methodName": "VerifyPropertyAvailability",
    "params": {
        "token_key": token_key,
        "token_secret": token_secret,
        "unit_id": "288515",
        "startdate": "08/01/2026",
        "enddate": "08/03/2026"
    }
}

print("Sending request to StreamlineVRS...")

try:
    response = requests.post(base_url, json=payload, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
except requests.exceptions.ConnectionError:
    print("ERROR: Could not connect. Check your STREAMLINE_BASE_URL.")
except requests.exceptions.Timeout:
    print("ERROR: Request timed out. Server may be unreachable.")
except Exception as e:
    print(f"ERROR: {e}")