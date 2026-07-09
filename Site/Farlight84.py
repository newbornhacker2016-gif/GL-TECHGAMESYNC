import os
import re
import sys
import requests
from bs4 import BeautifulSoup

def fetch_farlight_patch():
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
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Pull elements that could wrap an item row or dynamic item grouping block
        elements = soup.find_all(['div', 'li', 'a', 'p'])
        latest_date = None

        for el in elements:
            text = el.get_text(" ", strip=True)
            
            # Require the exact text signature keywords to match your announcement block
            if "UPDATE" in text.upper() or "PATCH NOTES" in text.upper():
                # Isolate the YYYY.MM.DD timestamp right next to it or embedded inside
                date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', text)
                if date_match:
                    # Parse out and reformat to YYYY-MM-DD
                    latest_date = date_match.group(1).replace('.', '-')
                    break
        
        # Fallback Strategy: If list objects are nested dynamically inside raw script templates
        if not latest_date:
            # Match sections where the patch string and a date string appear close together
            pattern = r'(?:UPDATE|PATCH NOTES)[^"\'\n]{0,100}\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b'
            matches = re.findall(pattern, response.text, re.IGNORECASE)
            if matches:
                latest_date = matches[0].replace('.', '-')
            else:
                # Direct lookup for the text segment right after an update mention
                reverse_pattern = r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b[^"\'\n]{0,100}(?:UPDATE|PATCH NOTES)'
                rev_matches = re.findall(reverse_pattern, response.text, re.IGNORECASE)
                if rev_matches:
                    latest_date = rev_matches[0].replace('.', '-')

        if not latest_date:
            print("Error: Could not isolate the specific update/patch notice timestamp.")
            sys.exit(1)

        print(f"Correctly Scraped Patch Date: '{latest_date}'")

        # Compare with the currently saved file content
        current_saved_date = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                current_saved_date = f.read().strip()
        
        # Overwrite file if the scraped date differs
        if latest_date != current_saved_date:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(latest_date)
            print(f"Updated {txt_filename}: '{current_saved_date}' -> '{latest_date}'")
        else:
            print(f"No changes needed. File remains synchronized: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_farlight_patch()
