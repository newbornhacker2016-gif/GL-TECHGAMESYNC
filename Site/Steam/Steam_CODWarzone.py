import os
import re
import sys
from datetime import datetime

# Call of Duty: Warzone App ID on Steam
APP_ID = "1962663"

# This file is produced by the GitHub Actions workflow, which runs the real
# `steamcmd` tool (the same one SteamDB itself uses) via:
#   steamcmd.sh +login anonymous +app_info_update 1 +app_info_print 1962663 +quit
# Warzone is a "DLC" type entry with no real installable depots/builds, so
# there's no buildid to track. steamcmd prints a summary line ABOVE the VDF
# block, e.g.:
#   AppID : 1962663, change number : 36926872/0, token 0, last change : Tue Jun 30 01:51:32 2026
# The "last change" timestamp here is the exact same official Steam PICS data
# that SteamDB displays as "Last Record Update" - so we can format it to match
# without ever touching SteamDB's (Cloudflare-protected) website.
RAW_APPINFO_FILE = "appinfo_raw.txt"

HISTORY_FILE = "Site/Steam/last_codwarzone_update.txt"
OUTPUT_FILE = "Steam/Steam Call of Duty Warzone.txt"

def get_latest_record_update():
    if not os.path.exists(RAW_APPINFO_FILE):
        print(f"ERROR: {RAW_APPINFO_FILE} not found. Did the steamcmd step run first?")
        return None

    with open(RAW_APPINFO_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    match = re.search(r"last change\s*:\s*(.+)", raw_text)
    if not match:
        print("Could not find a 'last change' entry in the steamcmd output.")
        return None

    raw_date_str = match.group(1).strip()

    try:
        # steamcmd prints a C ctime()-style string, e.g. "Tue Jun 30 01:51:32 2026"
        parsed = datetime.strptime(raw_date_str, "%a %b %d %H:%M:%S %Y")
    except ValueError as e:
        print(f"Could not parse 'last change' date '{raw_date_str}': {e}")
        return None

    # Format to match SteamDB's own display style, e.g. "30 June 2026 – 01:51:32 UTC"
    # GitHub Actions runners default to UTC, so this timestamp is already UTC.
    return parsed.strftime("%d %B %Y \u2013 %H:%M:%S UTC")

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
