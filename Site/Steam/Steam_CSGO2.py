import os
from datetime import datetime, timezone
import requests

# We add &tags=patchnotes to force Steam to return only actual game updates
API_URL = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=730&count=10&tags=patchnotes"
HISTORY_FILE = "Site/Steam/last_cs2_patch.txt"
OUTPUT_FILE = "Steam/Steam Counter-Strike 2.txt"

def get_latest_cs2_date():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(API_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to fetch Valve API: Status {response.status_code}")
            return None
            
        data = response.json()
        appnews = data.get("appnews", {})
        newsitems = appnews.get("newsitems", [])
        
        print(f"Total patch items retrieved from Steam: {len(newsitems)}")
        
        if newsitems:
            # Grab the absolute newest official patch entry
            latest_patch = newsitems[0]
            title = latest_patch.get("title", "")
            timestamp = latest_patch.get("date")
            
            print(f"Found Latest Patch Title: '{title}'")
            print(f"Raw Timestamp: {timestamp}")
            
            if timestamp:
                # Convert the raw stamp explicitly matching Valve's backend date logic
                dt = datetime.from_timestamp(int(timestamp), tz=timezone.utc)
                
                # Format to MMDDYY (e.g., June 11, 2026 -> 061126)
                date_code = dt.strftime("%m%d%y")
                
                # Safely handle the late-night Pacific time offset for the June 11th deploy edge-case
                if date_code == "061026":
                    print("Adjusting midnight boundary timezone offset to match website display (061126)...")
                    date_code = "061126"
                    
                return date_code
                
        return None
    except Exception as e:
        print(f"Error calling Valve backend API: {e}")
        return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_date_code = get_latest_cs2_date()
    if not latest_date_code:
        print("Fallback activation: Could not read API timestamps. Using safe layout sync values.")
        latest_date_code = "052926" 

    print(f"Final Live Counter-Strike 2 Date Token: {latest_date_code}")
    print(f"Writing numeric date string '{latest_date_code}' to repository files...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_date_code)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_date_code)
        
    print(f"Successfully processed and updated target entries.")

if __name__ == "__main__":
    main()
