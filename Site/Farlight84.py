import os
import re
import sys
import requests
from bs4 import BeautifulSoup

def fetch_farlight_patch():
    # Target URL matching the update tab
    url = "https://farlight84.farlightgames.com/news/index.html?tab=2"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    txt_filename = "Farlight84.txt"
    if not os.path.exists(txt_filename) and os.path.exists(os.path.join("..", txt_filename)):
        txt_path = os.path.join("..", txt_filename)
    else:
        txt_path = txt_filename

    try:
        print(f"Connecting to {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        raw_html = response.text
        latest_date = None

        # Strategy 1: Search the raw HTML and embedded scripts for a date pattern following "Update" or "Patch" keywords
        # This scans across any hidden JSON configurations or static arrays sent by the server.
        matches = re.findall(r'(?:UPDATE|PATCH[^"\'\n]*)\s*.*?([2][0][2-3][0-9][\./-][0-1][0-9][\./-][0-3][0-9])', raw_html, re.IGNORECASE)
        
        if matches:
            # Pick the most recent/first match and clean up delimiters to hyphenated formatting
            latest_date = matches[0].replace('.', '-').replace('/', '-')
            print(f"Located patch date via explicit data regex sweep: {latest_date}")
        
        # Strategy 2: If keyword regex fails, pull the absolute latest general date pattern inside the page source
        if not latest_date:
            all_dates = re.findall(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', raw_html)
            if all_dates:
                latest_date = all_dates[0].replace('.', '-').replace('/', '-')
                print(f"Located date via global fallback timestamp search: {latest_date}")

        # Strategy 3: Check standard BeautifulSoup text extraction across all tags
        if not latest_date:
            soup = BeautifulSoup(raw_html, 'html.parser')
            for el in soup.find_all(True):
                text = el.get_text(" ", strip=True)
                if "UPDATE" in text.upper() or "PATCH" in text.upper():
                    date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', text)
                    if date_match:
                        latest_date = date_match.group(1).replace('.', '-').replace('/', '-')
                        print(f"Located patch date via DOM string fallback: {latest_date}")
                        break

        if not latest_date:
            print("Error: Could not isolate an official update timestamp from page source or embedded data configurations.")
            sys.exit(1)

        print(f"Final Scraped Patch Date: '{latest_date}'")

        # Compare with the currently saved patch date
        current_saved_date = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                current_saved_date = f.read().strip()
        
        if latest_date != current_saved_date:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(latest_date)
            print(f"Updated {txt_filename}: '{current_saved_date}' -> '{latest_date}'")
        else:
            print(f"No update required. Local file is synchronized with the live site: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_farlight_patch()
