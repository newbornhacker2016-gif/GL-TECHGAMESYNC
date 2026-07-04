import os
import re
import sys

# Call of Duty: Warzone App ID on Steam
APP_ID = "1962663"

# This file is produced by the GitHub Actions workflow, which runs the real
# `steamcmd` tool (the same one SteamDB itself uses) via:
#   steamcmd.sh +login anonymous +app_info_update 1 +app_info_print 1962663 +quit
# Warzone is a "DLC" type entry with no real installable depots/builds, so
# there's no buildid to track. Instead we track Valve's own PICS
# "_change_number" - the same value SteamDB displays as "Last Changenumber".
# This is official Steam data, not scraped from SteamDB, so there's no
# Cloudflare/bot-blocking risk at all.
RAW_APPINFO_FILE = "appinfo_raw.txt"

HISTORY_FILE = "Site/Steam/last_codwarzone_changenumber.txt"
OUTPUT_FILE = "Steam/Steam Call of Duty Warzone.txt"

def get_latest_change_number():
    if not os.path.exists(RAW_APPINFO_FILE):
        print(f"ERROR: {RAW_APPINFO_FILE} not found. Did the steamcmd step run first?")
        return None

    with open(RAW_APPINFO_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    # VDF (Valve's config format) looks like:
    #   "1962663"
    #   {
    #       "_change_number"        "36926872"
    #       ...
    match = re.search(r'"_change_number"\s*"(\d+)"', raw_text)
    if match:
        return match.group(1).strip()

    print("Could not find '_change_number' in the steamcmd output.")
    return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_change_number = get_latest_change_number()
    if not latest_change_number:
        # No fake/placeholder fallback - fail loudly instead of
        # silently committing a bogus value.
        print("ERROR: Could not determine the latest Warzone changenumber. Aborting without writing files.")
        sys.exit(1)

    print(f"Discovered Latest Warzone Changenumber: {latest_change_number}")

    # Read previous version to avoid unnecessary git commits
    last_saved_change_number = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            last_saved_change_number = f.read().strip()

    if latest_change_number != last_saved_change_number:
        print(f"New update detected! Writing changenumber '{latest_change_number}' to repository files...")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_change_number)

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write(latest_change_number)

        print("Successfully updated target files.")
    else:
        print("No changenumber variance detected. Code execution clean.")

if __name__ == "__main__":
    main()
