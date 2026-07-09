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
    # Resolve correct relative file paths for locally vs on remote runner jobs
    if not os.path.exists(txt_filename) and os.path.exists(os.path.join("..", txt_filename)):
        txt_path = os.path.join("..", txt_filename)
    else:
        txt_path = txt_filename

    try:
        print(f"Connecting to Farlight 84 News board...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Farlight's DOM layout usually renders news lists in list items, anchors, or custom divs.
        # We parse elements structurally looking for title matches containing date formats (YYYY.MM.DD) or generic elements.
        elements = soup.find_all(['li', 'a', 'div', 'p'])
        latest_date = None

        for el in elements:
            text = el.get_text(" ", strip=True)
            
            # Target elements containing 'Update' or 'Patch Notes' phrases
            if ("UPDATE" in text.upper() or "PATCH NOTES" in text.upper()):
                # Match common pattern sequences found on their official site: YYYY.MM.DD
                date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', text)
                if date_match:
                    latest_date = date_match.group(1).replace('.', '-') # Clean format to YYYY-MM-DD
                    break

        # Fallback case: if raw HTML text matching fails due to Client-side JavaScript rendering,
        # we pull directly from common API paths used by their framework if detectable.
        if not latest_date:
            print("Web structure analysis fallback triggered...")
            # We try a general regex scan across the whole response content body
            all_dates = re.findall(r'\b(20\d{2}\.\d{2}\.\d{2})\b', response.text)
            if all_dates:
                latest_date = all_dates[0].replace('.', '-')

        if not latest_date:
            print("Could not isolate a recent patch update date from the target layout.")
            sys.exit(0)

        print(f"Scraped Date from Web: '{latest_date}'")

        # Track existing file changes
        current_saved_date = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                current_saved_date = f.read().strip()
        
        if latest_date != current_saved_date:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(latest_date)
            print(f"Updated {txt_filename}: '{current_saved_date}' -> '{latest_date}'")
        else:
            print(f"No update required. Already matches live site: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_farlight_patch()
