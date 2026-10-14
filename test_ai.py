
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
url = os.getenv("GEMINI_API_URL")

if not api_key or not url:
    raise SystemExit("Missing API key or URL in .env")

payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": (
                        "Extract structured data from this casino offer: "
                        "'100% welcome bonus up to 500 EUR, "
                        "minimum deposit 20 EUR, wagering 35x'. "
                        "Return only JSON with these fields: "
                        "welcome_bonus, wagering_requirement, "
                        "minimum_deposit."
                    )
                }
            ]
        }
    ],
    "generationConfig": {
        "responseMimeType": "application/json"
    }
}

response = requests.post(
    url,
    headers={
        "Content-Type": "application/json",
        "X-goog-api-key": api_key
    },
    json=payload,
    timeout=45
)

print("HTTP status:", response.status_code)

if not response.ok:
    print(response.text[:2000])
    raise SystemExit(1)

data = response.json()
result = data["candidates"][0]["content"]["parts"][0]["text"]

print(json.dumps(json.loads(result), indent=2))
