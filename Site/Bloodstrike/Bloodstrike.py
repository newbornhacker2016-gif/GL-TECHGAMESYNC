import os
import re
import requests
from bs4 import BeautifulSoup

MAIN_URL = "https://www.blood-strike.com/news/update/"
HISTORY_FILE = "Site/Bloodstrike/last_bloodstrike_patch.txt"
OUTPUT_FILE = "Bloodstrike.txt"

def get_latest_bloodstrike_date():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(MAIN_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to access Blood Strike page: {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Scrape all headings/titles on the update grid layout
        # (NetEase news feeds usually bundle titles inside h3, h2, or custom list classes)
        elements = soup.find_all(['h3', 'h2', 'a', 'p'])
        
        for item in elements:
            text = item.get_text().strip()
            
            # Target matching phrases like "Version Update Announcement 2026/06/04"
            if "version update announcement" in text.lower():
                # Extract the YYYY/MM/DD format sequence
                match = re.search(r'(\d{4})[/.-](\d{2})[/.-](\d{2})', text)
                if match:
                    year, month, day = match.group(1), match.group(2), match.group(3)
                    return f"{year}.{month}.{day}"
                    
        # Fallback target scanner: check the raw text block elements on the page if classes shift
        page_text = soup.get_text()
        matches = re.findall(r'Version Update Announcement\s*(\d{4})[/.-](\d{2})[/.-](\d{2})', page_text, re.IGNORECASE)
        if matches:
            year, month, day = matches[0]
            return f"{year}.{month}.{day}"
            
        return None
    except Exception as e:
        print(f"Error parsing components: {e}")
        return None

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_version = get_latest_bloodstrike_date()
    if not latest_version:
        print("Could not isolate a valid 'Version Update Announcement' date stamp.")
        # If site fails to parse due to client-side JS rendering, default to a robust fallback tag
        print("Using layout date reference sync placeholder.")
        return

    print(f"Discovered Live Update Date: {latest_version}")
    
    # Force write configuration to pop data immediately on manual trigger run
    print(f"Writing clean target update sequence '{latest_version}' to tracking file...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_version)
        
    print(f"Successfully updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
