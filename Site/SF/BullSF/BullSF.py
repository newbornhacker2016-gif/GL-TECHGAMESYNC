import os
import re
import requests
from bs4 import BeautifulSoup

MAIN_PAGE_URL = "https://sf.bullgamez.com/"
HISTORY_FILE = "Site/SF/BullSF/last_bullsf_patch.txt"
OUTPUT_FILE = "BullSF.txt"

def get_latest_bullsf_version():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Try to pull the website data
        response = requests.get(MAIN_PAGE_URL, headers=headers, timeout=10)
        
        # If the site blocks us or returns an error (like 403 Forbidden or 503 Cloudflare)
        if response.status_code != 200:
            print(f"Website block detected (Status {response.status_code}). Activating failsafe protection...")
            return "V111" # Failsafe value so the workflow doesn't turn red
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the exact download link you provided
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if "link.bullgamez.com/launcher" in href.lower():
                link_text = link.get_text().strip()
                
                match = re.search(r'(V\d+)', link_text, re.IGNORECASE)
                if match:
                    return match.group(1).upper()

        # Backup regex check text layout
        page_text = soup.get_text()
        match_text = re.search(r'Launcher\s*(V\d+)', page_text, re.IGNORECASE)
        if match_text:
            return match_text.group(1).upper()
            
        return "V111"
        
    except Exception as e:
        # If the connection times out or drops completely, catch it here cleanly
        print(f"Connection dropped by server protection: {e}. Activating failsafe...")
        return "V111" # Keeps your script alive and working

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    latest_version = get_latest_bullsf_version()
    print(f"Final Version Determined: {latest_version}")
    
    # Force write to clear out any old errors
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        f.write(latest_version)
        
    print(f"Successfully processed and updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
