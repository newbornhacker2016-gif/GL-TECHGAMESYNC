import os
import re
import requests
from bs4 import BeautifulSoup

# URLs
MAIN_URL = "https://www.dota2.com/patches"

# Adjusted Paths relative to the root directory where the GitHub Action runs
HISTORY_FILE = "Site/Steam/last_patch.txt" 
OUTPUT_FILE = "Steam/Steam Dota 2.txt"

def get_latest_patch_url():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    response = requests.get(MAIN_URL, headers=headers)
    if response.status_code != 200:
        print("Failed to access Dota 2 patches page")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    patch_urls = []
    for link in links:
        href = link['href']
        if "/patches/7." in href:
            if href.startswith("/"):
                href = f"https://www.dota2.com{href}"
            patch_urls.append(href)
            
    return patch_urls[0] if patch_urls else None

def extract_version_number(url):
    # Example URL: https://www.dota2.com/patches/7.41c
    # This extracts anything after the /patches/ folder matching a number format
    match = re.search(r'patches/(7\.\d+[a-z]?)', url.lower())
    if match:
        return match.group(1)
        
    # Fallback: just look for the first string pattern that looks like 7.XX
    match_fallback = re.search(r'(7\.\d+[a-z]?)', url.lower())
    if match_fallback:
        return match_fallback.group(1)
        
    return "Unknown Version"

def main():
    # Ensure the target folders exist before trying to save files
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_url = get_latest_patch_url()
    if not latest_url:
        print("No patch URL found.")
        return

    print(f"Current live patch URL: {latest_url}")
    
    # Extract just the clean version string (e.g., "7.41c")
    version_only = extract_version_number(latest_url)
    print(f"Extracted Patch Version: {version_only}")
    
    # --- WE REMOVE THE SAFETY GATE CHECK FOR THE FIRST RUN TO FORCE THE CLEAN OVERWRITE ---
    print(f"Writing clean version number '{version_only}' to text file...")
    
    # Wipes out the full page paragraphs completely and leaves ONLY the version number
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(version_only)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_url)
        
    print(f"Text-only version number saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
