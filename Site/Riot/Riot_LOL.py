import os
import re
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

# The raw HTML patch notes tag page
MAIN_URL = "https://www.leagueoflegends.com/en-ph/news/tags/patch-notes/"
HISTORY_FILE = "Site/Riot/last_lol_patch.txt"
OUTPUT_FILE = "LeagueOfLegend.txt"

def get_latest_lol_patch_url():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(MAIN_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to access League page: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for any hyperlink containing "patch" and "notes" in the URL structure
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if "patch" in href.lower() and "notes" in href.lower():
                # Format to absolute link structure
                if href.startswith("/"):
                    href = f"https://www.leagueoflegends.com{href}"
                return href
                
        return None
    except Exception as e:
        print(f"Error scanning page elements: {e}")
        return None

def extract_version_number(url):
    # Extracts numbers following the word 'patch' (e.g. patch-26-11 -> 26.11)
    match = re.search(r'patch-(\d+)[-.](\d+)', url.lower())
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    
    # Fallback pattern match
    match_fallback = re.search(r'(\d+)[-.](\d+)', url)
    if match_fallback:
        return f"{match_fallback.group(1)}.{match_fallback.group(2)}"
        
    return "Unknown Version"

def is_time_allowed_pht():
    # PHT is UTC+8
    pht_zone = timezone(timedelta(hours=8))
    now_pht = datetime.now(pht_zone)
    
    current_day = now_pht.weekday() # Monday=0, Tuesday=1, Wednesday=2...
    current_hour = now_pht.hour
    
    print(f"Current Time (PHT): {now_pht.strftime('%A %I:%M %p')}")
    
    # Block updates on Monday and Tuesday completely
    if current_day < 2:
        return False
    # Block updates on Wednesday before 11:00 AM PHT
    if current_day == 2 and current_hour < 11:
        return False
        
    # Allow updates on Wednesday after 11 AM, Thursday, Friday, Saturday, Sunday
    return True

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_url = get_latest_lol_patch_url()
    if not latest_url:
        print("Could not isolate a valid patch link from the page layout.")
        return

    print(f"Discovered Live Patch URL: {latest_url}")
    version_only = extract_version_number(latest_url)
    print(f"Extracted Patch Version: {version_only}")
    
    # Read the previous url we saved
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()

    # Check if a new patch link exists
    if latest_url != last_saved_url:
        print("New patch detected on website!")
        
        # Apply the Wednesday 11:00 AM PHT gate rule
        if not is_time_allowed_pht():
            print("Holding off update! It is not Wednesday at 11:00 AM PHT yet.")
            return
            
        print(f"Time gate passed. Writing clean version number '{version_only}' to text file...")
        
        # Wipes out the file completely and replaces it with just the version number
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(version_only)
            
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            f.write(latest_url)
            
        print(f"Successfully saved to {OUTPUT_FILE}")
    else:
        print("No new patch variance detected on the website.")

if __name__ == "__main__":
    main()
