import os
import re
import sys
import requests

# Call of Duty: Warzone App ID on Steam
APP_ID = "1962663"
PAGE_URL = f"https://steamdb.info/app/{APP_ID}/"

HISTORY_FILE = "Site/Steam/last_codwarzone_update.txt"
OUTPUT_FILE = "Steam/Steam Call of Duty Warzone.txt"

def get_latest_record_update():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        response = requests.get(PAGE_URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"Failed to fetch SteamDB page: Status {response.status_code}")
            return None

        html = response.text

        # The app page renders a table row like:
        #   Last Record Update   4 June 2026 – 22:34:33 UTC (...)
        # Grab the first date/time pattern that appears after that label.
        match = re.search(
            r"Last Record Update.{0,400}?(\d{1,2}\s+[A-Za-z]+\s+\d{4}\s*[\u2013-]\s*\d{2}:\d{2}:\d{2}\s*UTC)",
            html,
            re.DOTALL,
        )
        if match:
            return match.group(1).strip()

        print("Could not locate 'Last Record Update' timestamp in the page HTML.")
        return None
    except Exception as e:
        print(f"Error fetching/parsing SteamDB page: {e}")
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
