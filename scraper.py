
import os
import re
import json
import time
import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

# Load environment variables
load_dotenv(override=True)

SOURCE_URL = (
    "https://betproof.co.za/casino-bonuses-south-africa/"
    "sign-up-bonus-south-africa/"
)

USER_AGENT = "CasinoBonusAssessmentBot/1.0"

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = os.getenv("GEMINI_API_URL")

if not API_KEY or not API_URL:
    raise SystemExit(
        "Missing GEMINI_API_KEY or GEMINI_API_URL in .env"
    )


# ---------------------------------------
# STEP 1: CHECK ROBOTS.TXT
# ---------------------------------------

def check_robots(url):
    parsed = urlparse(url)

    robots_url = (
        f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    )

    response = requests.get(
        robots_url,
        headers={"User-Agent": USER_AGENT},
        timeout=(10, 20)
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Cannot verify robots.txt: HTTP "
            f"{response.status_code}"
        )

    robots = RobotFileParser()
    robots.parse(response.text.splitlines())

    if not robots.can_fetch(USER_AGENT, url):
        raise RuntimeError(
            "Scraping disallowed by robots.txt"
        )

    print("Robots.txt check passed.")


# ---------------------------------------
# STEP 2: FETCH CASINO DATA
# ---------------------------------------

def fetch_casinos():
    check_robots(SOURCE_URL)

    print("Fetching casino bonus page...")

    response = requests.get(
        SOURCE_URL,
        headers={"User-Agent": USER_AGENT},
        timeout=(10, 30)
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    tables = soup.find_all("table")

    print(f"Found {len(tables)} HTML tables.")

    for table in tables:
        rows = table.find_all("tr")

        if len(rows) < 4:
            continue

        headers = [
            cell.get_text(" ", strip=True).lower()
            for cell in rows[0].find_all(["th", "td"])
        ]

        if not (
            any("bonus" in h for h in headers)
            and any("wager" in h for h in headers)
            and any("deposit" in h for h in headers)
        ):
            continue

        print("Matching bonus table found.")

        casinos = []

        for row in rows[1:]:
            cells = [
                cell.get_text(" ", strip=True)
                for cell in row.find_all(["td", "th"])
            ]

            if len(cells) < 4:
                continue

            casino_name = re.sub(
                r"\s*Claim\s*→?\s*$",
                "",
                cells[0],
                flags=re.IGNORECASE
            ).strip()

            if not casino_name:
                continue

            casinos.append({
                "casino": casino_name,
                "raw_bonus": cells[1],
                "raw_wagering": cells[2],
                "raw_deposit": cells[3],
                "source_url": SOURCE_URL
            })

            print(f"Extracted: {casino_name}")

            if len(casinos) == 3:
                break

        if len(casinos) == 3:
            return casinos

    raise RuntimeError(
        "Could not extract three casinos "
        "from the source table."
    )


# ---------------------------------------
# STEP 3: PROCESS DATA WITH GEMINI AI
# ---------------------------------------

def process_with_ai(casinos):
    prompt = f"""
You are a structured data extraction assistant.

Convert these scraped casino bonus records
into a JSON array.

Return exactly these fields:
- casino
- welcome_bonus
- wagering_requirement
- minimum_deposit
- source_url

Rules:
1. Do not invent information.
2. Preserve original currencies and amounts.
3. Preserve multiple wagering conditions.
4. Remove navigation text such as Claim.
5. Use null for missing information.
6. Keep casino names and source URLs unchanged.
7. Return exactly three objects.
8. Return valid JSON only.

Input:
{json.dumps(casinos, ensure_ascii=False)}
"""

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0,
            "maxOutputTokens": 4096
        }
    }

    for attempt in range(1, 4):
        try:
            print(
                f"Gemini request attempt {attempt}/3..."
            )

            response = requests.post(
                API_URL,
                headers={
                    "Content-Type": "application/json",
                    "X-goog-api-key": API_KEY
                },
                json=payload,
                timeout=(10, 90)
            )

            response.raise_for_status()

            result = response.json()

            candidates = result.get("candidates", [])

            if not candidates:
                raise RuntimeError(
                    "Gemini returned no candidates: "
                    + json.dumps(result)[:500]
                )

            parts = candidates[0].get(
                "content", {}
            ).get("parts", [])

            content = "".join(
                part.get("text", "")
                for part in parts
            )

            if not content:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            structured = json.loads(content)

            print("Gemini successfully processed data.")

            return structured

        except requests.exceptions.Timeout:
            print("Gemini request timed out.")

            if attempt == 3:
                raise RuntimeError(
                    "Gemini timed out after three attempts."
                )

            time.sleep(attempt * 2)

        except requests.exceptions.HTTPError:
            print(
                "Gemini HTTP error:",
                response.status_code
            )
            print(response.text[:1000])
            raise

        except requests.exceptions.RequestException as error:
            raise RuntimeError(
                f"Gemini network error: {error}"
            ) from error

        except json.JSONDecodeError as error:
            raise RuntimeError(
                "Gemini returned invalid JSON."
            ) from error

    raise RuntimeError("Gemini processing failed.")


# ---------------------------------------
# STEP 4: VALIDATE AI OUTPUT
# ---------------------------------------

def validate_results(raw, structured):
    if not isinstance(structured, list):
        raise ValueError(
            "Gemini response must be a JSON array."
        )

    if len(structured) != len(raw):
        raise ValueError(
            "Incorrect number of casino records."
        )

    required = {
        "casino",
        "welcome_bonus",
        "wagering_requirement",
        "minimum_deposit",
        "source_url"
    }

    for original, item in zip(raw, structured):
        if not isinstance(item, dict):
            raise ValueError("Invalid casino record.")

        if not required.issubset(item):
            raise ValueError("Missing required fields.")

        if item["casino"] != original["casino"]:
            raise ValueError(
                "Casino name changed unexpectedly."
            )

        if item["source_url"] != SOURCE_URL:
            raise ValueError(
                "Source URL changed unexpectedly."
            )

        fields = (
            ("welcome_bonus", "raw_bonus"),
            ("wagering_requirement", "raw_wagering"),
            ("minimum_deposit", "raw_deposit")
        )

        for output_key, source_key in fields:
            output_value = item[output_key]
            source_value = original[source_key]

            if output_value is not None and not isinstance(
                output_value, (str, int, float)
            ):
                raise ValueError(
                    f"Invalid {output_key} type "
                    f"for {item['casino']}"
                )

            source_numbers = set(
                re.findall(r"\d+", source_value)
            )

            output_numbers = set(
                re.findall(r"\d+", str(output_value or ""))
            )

            if not output_numbers.issubset(source_numbers):
                raise ValueError(
                    f"Unexpected numbers in {output_key} "
                    f"for {item['casino']}"
                )

        print(f"Validated: {item['casino']}")

    return structured


# ---------------------------------------
# STEP 5: SAVE JSON FILE
# ---------------------------------------

def save_json(casinos):
    output_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "casinos.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            casinos,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"Successfully generated {output_file}")


# ---------------------------------------
# MAIN PROGRAM
# ---------------------------------------

def main():
    print("=" * 45)
    print("CASINO BONUS SCRAPER")
    print("=" * 45)

    raw_casinos = fetch_casinos()

    print(
        f"\nExtracted {len(raw_casinos)} casinos."
    )

    print("\nSending extracted data to Gemini...")

    structured = process_with_ai(raw_casinos)

    print("\nValidating AI output...")

    validated = validate_results(
        raw_casinos,
        structured
    )

    save_json(validated)

    print("\nSCRAPING COMPLETED SUCCESSFULLY!")

    for casino in validated:
        print(f"\nCasino: {casino['casino']}")
        print(f"Bonus: {casino['welcome_bonus']}")
        print(
            f"Wagering: "
            f"{casino['wagering_requirement']}"
        )
        print(
            f"Minimum deposit: "
            f"{casino['minimum_deposit']}"
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}")
        raise SystemExit(1)
