import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

MAIN_URL = "https://www.counter-strike.net/news/updates"
HISTORY_FILE = "Site/Steam/last_cs2_patch.txt"
OUTPUT_FILE = "Steam/Steam Counter-Strike 2.txt"

def get_latest_cs2_date():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(MAIN_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to access CS2 updates page: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Valve structures patch date headers inside a specific container class
        # Look for elements matching their update post date layouts
        date_elements = soup.find_all(class_=re.compile(r'inner_PostDate|postDate|date', re.IGNORECASE))
        
        for elem in date_elements:
            date_text = elem.get_text().strip()
            # Expecting format variants like "May 29, 2026" or "May 29 2026"
            try:
                # Clean up commas or extra spacing to guarantee accurate datetime parsing
                clean_date = date_text.replace(',', '').replace('  ', ' ')
                dt = datetime.strptime(clean_date, "%B %d %Y")
                # Format to MMDDYY (e.g., May 29, 2026 -> 052926)
                return dt.strftime("%m%d%y")
            except ValueError:
                continue

        # Fallback raw regex check across entire page text if structural element names shift
        page_text = soup.get_text()
        months_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)'
        match = re.search(months_pattern + r'\s+\d{1,2},?\s+\d{4}', page_text, re.IGNORECASE)
        if match:
            clean_date = match.group(0).replace(',', '').replace('  ', ' ')
            dt = datetime.strptime(clean_date, "%B %d %Y")
            return dt.strftime("%m%d%y")

        return None
    except Exception as e:
        print(f"Error extracting CS2 patch date: {e}")
        return None

def main():
    if os.path.dirname(HISTORY_FILE):
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if os.path.dirname(OUTPUT_FILE):
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_date_code = get_latest_cs2_date()
    if not latest_date_code:
        print("Could not isolate a valid patch date header sequence.")
        return

    print(f"Live Counter-Strike 2 Date Token: {latest_date_code}")
    print(f"Writing numeric date string '{latest_date_code}' to repository files...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_date_code)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_date_code)
        
    print(f"Successfully processed and updated target arrays.")

if __name__ == "__main__":
    main()
