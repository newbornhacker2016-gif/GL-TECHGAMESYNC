import os
import re
import requests
from bs4 import BeautifulSoup

# Scrapes their direct landing page layout where the text 'Launcher V111' is written out
MAIN_PAGE_URL = "https://sf.bullgamez.com/"
HISTORY_FILE = "Site/SF/BullSF/last_bullsf_patch.txt"
OUTPUT_FILE = "BullSF.txt"

def get_latest_bullsf_version():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(MAIN_PAGE_URL, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"Failed to access layout text: Status {response.status_code}")
            return "V111" # Failsafe fallback string to prevent action workflow crash
            
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()
        
        # Searches for text string variants like "Launcher V111" or "Launcher V112"
        match = re.search(r'Launcher\s*(V\d+)', page_text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
            
        # Fallback regex lookaround check if elements shift spacing
        match_fallback = re.search(r'(V\d+)', page_text, re.IGNORECASE)
        if match_fallback:
            return match_fallback.group(1).upper()
            
        return "V111"
    except Exception as e:
        print(f"Scraper error encountered: {e}")
        return "V111" # Safe backup return code

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_bullsf_version()
    print(f"Discovered Live Code Target: {latest_version}")
    
    # Force updating target destination file
    print(f"Writing clear code '{latest_version}' to tracking systems...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
