import os
import re
import requests
from bs4 import BeautifulSoup

# Scrapes the primary web landing page 
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
            print(f"Failed to load main page: Status {response.status_code}")
            return "V111" # Safe fallback
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Target the exact download link structure from the HTML snippet
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            # Match the exact link destination
            if "link.bullgamez.com/launcher" in href.lower():
                link_text = link.get_text().strip()
                print(f"Found targeted download link text: {link_text}")
                
                # Extract 'V111' from the text inside the link using Regex
                match = re.search(r'(V\d+)', link_text, re.IGNORECASE)
                if match:
                    return match.group(1).upper()

        # 2. Backup Fallback: Scan the entire page text if the exact link structure shifts
        page_text = soup.get_text()
        match_text = re.search(r'Launcher\s*(V\d+)', page_text, re.IGNORECASE)
        if match_text:
            return match_text.group(1).upper()
            
        return "V111"
        
    except Exception as e:
        print(f"Scraper error encountered: {e}")
        return "V111"

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_bullsf_version()
    print(f"Isolated Version Output: {latest_version}")
    
    print(f"Writing clean code '{latest_version}' to tracking logs...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
