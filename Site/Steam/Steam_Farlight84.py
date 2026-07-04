import os
import sys
import requests

# Farlight 84 App ID on Steam
APP_ID = "1928420"

# Real, public, unauthenticated API that mirrors steamcmd's app_info_print data.
# Docs: https://www.steamcmd.net/ | Source: https://github.com/steamcmd/api
API_URL = f"https://api.steamcmd.net/v1/info/{APP_ID}"

HISTORY_FILE = "Site/Steam/last_farlight84_patch.txt"
OUTPUT_FILE = "Steam/Steam Farlight84.txt"

def get_latest_farlight84_build_id():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(API_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch SteamCMD API: Status {response.status_code}")
            return None

        data = response.json()

        if data.get("status") != "success":
            print(f"SteamCMD API returned non-success status: {data.get('status')}")
            return None

        app_data = data.get("data", {}).get(APP_ID, {})
        depots = app_data.get("depots", {})
        branches = depots.get("branches", {})
        public_branch = branches.get("public", {})
        build_id = public_branch.get("buildid")

        if build_id:
            return str(build_id).strip()

        print("Could not locate 'depots.branches.public.buildid' in API response.")
        return None
    except Exception as e:
        print(f"Error extracting Build ID from SteamCMD API: {e}")
        return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_build_id = get_latest_farlight84_build_id()
    if not latest_build_id:
        # No fake/placeholder fallback anymore - fail loudly instead of
        # silently committing a bogus buildID like "14000000".
        print("ERROR: Could not determine the latest Farlight 84 buildID. Aborting without writing files.")
        sys.exit(1)

    print(f"Discovered Live Farlight 84 Build ID: {latest_build_id}")
    
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
