import os
import re
import requests
from bs4 import BeautifulSoup

# The official Valorant Game Updates feed
MAIN_URL = "https://playvalorant.com/en-us/news/game-updates/"
HISTORY_FILE = "Site/Riot/last_valo_patch.txt"
OUTPUT_FILE = "Valorant.txt"

def get_latest_valo_patch_url():
    try:
        response = requests.get(MAIN_URL, timeout=15)
        if response.status_code != 200:
            print(f"Failed to access Valorant page: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for any link containing "patch-notes" in the URL string
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if "patch-notes" in href.lower() or "patch" in href.lower():
                # Format to absolute link structure if it's relative
                if href.startswith("/"):
                    href = f"https://playvalorant.com{href}"
                return href
                
        return None
    except Exception as e:
        print(f"Error scanning page elements: {e}")
        return None

def extract_version_number(url):
    # Example URL: https://playvalorant.com/en-us/news/game-updates/valorant-patch-notes-12-02/
    # We want to extract "12-02" and turn it into "12.02"
    match = re.search(r'notes-(\d+)[-.](\d+)', url.lower())
    if match:
        return f"{match.group(1)}.{match.group(2)}"
        
    # Fallback pattern if URL formatting changes slightly
    match_fallback = re.search(r'patch-(\d+)[-.](\d+)', url.lower())
    if match_fallback:
        return f"{match_fallback.group(1)}.{match_fallback.group(2)}"
        
    # Last resort: find any pair of double numbers
    match_numbers = re.search(r'(\d+)[-.](\d+)', url)
    if match_numbers:
        return f"{match_numbers.group(1)}.{match_numbers.group(2)}"
        
    return "Unknown Version"

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_url = get_latest_valo_patch_url()
    if not latest_url:
        print("Could not isolate a valid patch link from the page layout.")
        return

    print(f"Discovered Live Patch URL: {latest_url}")
    version_only = extract_version_number(latest_url)
    print(f"Extracted Patch Version: {version_only}")
    
    print(f"Writing clean version number '{version_only}' to text file...")
    
    # Writes ONLY the clean version string to the text file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(version_only)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_url)
        
    print(f"Successfully saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
