import os
import re
import requests
from bs4 import BeautifulSoup

# The raw HTML patch notes tag page
MAIN_URL = "https://www.leagueoflegends.com/en-ph/news/tags/patch-notes/"
HISTORY_FILE = "Site/Riot/last_lol_patch.txt"
OUTPUT_FILE = "LeagueOfLegend.txt"

def get_latest_lol_patch_url():
    try:
        response = requests.get(MAIN_URL, timeout=15)
        if response.status_code != 200:
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

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_url = get_latest_lol_patch_url()
    if not latest_url:
        print("Could not isolate a valid patch link from the page layout.")
        return

    print(f"Discovered Live Patch URL: {latest_url}")
    version_only = extract_version_number(latest_url)
    print(f"Extracted Patch Version: {version_only}")
    
    # --- TEMPORARILY REMOVED SAFETY GATE TO FORCE THE OVERWRITE ---
    print(f"Writing clean version number '{version_only}' to text file...")
    
    # Wipes out the 694 lines completely and replaces it with just the version number
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(version_only)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_url)
        
    print(f"Successfully saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
