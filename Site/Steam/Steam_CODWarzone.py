import os
import re
import sys
import time
import cloudscraper

# Call of Duty: Warzone App ID on Steam
APP_ID = "1962663"
PAGE_URL = f"https://steamdb.info/app/{APP_ID}/"

HISTORY_FILE = "Site/Steam/last_codwarzone_update.txt"
OUTPUT_FILE = "Steam/Steam Call of Duty Warzone.txt"

MAX_ATTEMPTS = 4
RETRY_DELAY_SECONDS = 8

def get_latest_record_update():
    # cloudscraper mimics a real browser's TLS/JS fingerprint well enough to
    # get past Cloudflare's bot-check, which a plain `requests` GET cannot do
    # (SteamDB blocks most datacenter/CI IP ranges, including GitHub Actions).
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    last_error = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = scraper.get(PAGE_URL, timeout=25)
            if response.status_code == 200:
                html = response.text

                # The app page renders a table row like:
                #   Last Record Update   4 June 2026 – 22:34:33 UTC (...)
                match = re.search(
                    r"Last Record Update.{0,400}?(\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[\u2013-]\s*\d{2}:\d{2}:\d{2}\s*UTC)",
                    html,
                    re.DOTALL,
                )
                if match:
                    return match.group(1).strip()

                last_error = "Could not locate 'Last Record Update' timestamp in the page HTML."
            else:
                last_error = f"Status {response.status_code}"

        except Exception as e:
            last_error = str(e)

        print(f"Attempt {attempt}/{MAX_ATTEMPTS} failed to fetch SteamDB page: {last_error}")
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
