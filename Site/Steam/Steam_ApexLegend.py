import os
import re
import sys

# Apex Legends App ID on Steam
APP_ID = "1172470"

# This file is produced by the GitHub Actions workflow, which runs the real
# `steamcmd` tool (the same one SteamDB itself uses) via:
#   steamcmd.sh +login anonymous +app_info_update 1 +app_info_print 1172470 +quit
RAW_APPINFO_FILE = "appinfo_raw.txt"

HISTORY_FILE = "Site/Steam/last_apexlegends_patch.txt"
OUTPUT_FILE = "Steam/Steam Apex Legends.txt"

def get_latest_apex_build_id():
    if not os.path.exists(RAW_APPINFO_FILE):
        print(f"ERROR: {RAW_APPINFO_FILE} not found. Did the steamcmd step run first?")
        return None

    with open(RAW_APPINFO_FILE, "r", encoding="utf-8", errors="ignore") as f:
        raw_text = f.read()

    # Look inside the "branches" -> "public" block for its "buildid" value.
    # VDF (Valve's config format) looks like:
    #   "branches"
    #   {
    #       "public"
    #       {
    #           "buildid"       "22561622"
    #           ...
    match = re.search(r'"public"\s*\{[^{}]*?"buildid"\s*"(\d+)"', raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    print("Could not find a 'public' branch buildid in the steamcmd output.")
    return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_build_id = get_latest_apex_build_id()
    if not latest_build_id:
        # No fake/placeholder fallback - fail loudly instead of
        # silently committing a bogus buildID.
        print("ERROR: Could not determine the latest Apex Legends buildID. Aborting without writing files.")
        sys.exit(1)

    print(f"Discovered Live Apex Legends Build ID: {latest_build_id}")

    # Read previous version to avoid unnecessary git commits
    last_saved_build = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            last_saved_build = f.read().strip()

    if latest_build_id != last_saved_build:
        print(f"New update detected! Writing buildID '{latest_build_id}' to repository files...")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(latest_build_id)

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write(latest_build_id)

        print("Successfully updated target files.")
    else:
        print("No buildID variance detected. Code execution clean.")

if __name__ == "__main__":
    main()
