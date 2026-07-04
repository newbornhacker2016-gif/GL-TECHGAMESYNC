import os
import re
import sys
import time
import requests
import cloudscraper

# Call of Duty: Warzone App ID on Steam
APP_ID = "1962663"
PAGE_URL = f"https://steamdb.info/app/{APP_ID}/"

# Jina AI's free Reader proxy fetches the page server-side (from its own
# infrastructure, not our CI runner's IP) and returns clean text. This gets
# around SteamDB's Cloudflare rule that blocks whole cloud/CI IP ranges
# (GitHub Actions included) outright, which no amount of header/UA tuning on
# our end can fix. Docs: https://jina.ai/reader
JINA_READER_URL = f"https://r.jina.ai/{PAGE_URL}"

HISTORY_FILE = "Site/Steam/last_codwarzone_update.txt"
OUTPUT_FILE = "Steam/Steam Call of Duty Warzone.txt"

MAX_ATTEMPTS = 4
RETRY_DELAY_SECONDS = 8

LAST_RECORD_UPDATE_PATTERN = re.compile(
    r"Last Record Update.{0,400}?(\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[\u2013-]\s*\d{2}:\d{2}:\d{2}\s*UTC)",
    re.DOTALL,
)

def try_via_jina_reader():
    try:
        response = requests.get(JINA_READER_URL, timeout=30)
        if response.status_code != 200:
            print(f"Jina Reader proxy fetch failed: Status {response.status_code}")
            return None

        match = LAST_RECORD_UPDATE_PATTERN.search(response.text)
        if match:
            return match.group(1).strip()

        print("Jina Reader fetch succeeded but 'Last Record Update' pattern not found.")
        return None
    except Exception as e:
        print(f"Jina Reader proxy fetch error: {e}")
        return None

def try_via_direct_cloudscraper():
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )
    try:
        response = scraper.get(PAGE_URL, timeout=25)
        if response.status_code != 200:
            print(f"Direct cloudscraper fetch failed: Status {response.status_code}")
            return None

        match = LAST_RECORD_UPDATE_PATTERN.search(response.text)
        if match:
            return match.group(1).strip()

        print("Direct fetch succeeded but 'Last Record Update' pattern not found.")
        return None
    except Exception as e:
        print(f"Direct cloudscraper fetch error: {e}")
        return None

def get_latest_record_update():
    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        result = try_via_jina_reader()
        if result:
            return result

        result = try_via_direct_cloudscraper()
        if result:
            return result

        last_error = "Both Jina Reader proxy and direct fetch failed."
        print(f"Attempt {attempt}/{MAX_ATTEMPTS}: {last_error}")
        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_DELAY_SECONDS)

    print(f"All {MAX_ATTEMPTS} attempts failed. Last error: {last_error}")
    return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_update = get_latest_record_update()
    if not latest_update:
        # No fake/placeholder fallback - fail loudly instead of
        # silently committing a bogus value.
        print("ERROR: Could not determine the latest Warzone record update timestamp. Aborting without writing files.")
        sys.exit(1)

    print(f"Discovered Latest Warzone Record Update: {latest_update}")

    # Read previous version to avoid unnecessary git commits
    last_saved_update = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            last_saved_update = f.read().strip()

    if latest_update != last_saved_update:
        print(f"New update detected! Writing '{latest_update}' to repository files...")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_update)

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write(latest_update)

        print("Successfully updated target files.")
    else:
        print("No update variance detected. Code execution clean.")

if __name__ == "__main__":
    main()
