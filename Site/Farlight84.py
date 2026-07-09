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
        
        raw_html = response.text
        latest_date = None

        # Extract all dates from the source code in sequence order (e.g. ['2026.02.05', '2025.07.28'])
        all_dates = re.findall(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', raw_html)
        
        # Look for news blocks inside script configurations or templates
        # Splitting by common JSON data objects or entry definitions inside the code
        blocks = re.split(r'(?:{"id"|title|{\s*url\s*:)', raw_html)
        
        for block in blocks:
            # Check if this block contains an explicit Update indicator
            if "UPDATE" in block.upper() or "PATCH NOTES" in block.upper():
                # Isolate the exact timestamp linked within THIS block
                date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', block)
                if date_match:
                    latest_date = date_match.group(1).replace('.', '-')
                    print(f"Locked onto Patch block date: {latest_date}")
                    break

        # Fallback tracking if split block detection misses
        if not latest_date:
            # Look up lines containing both an update keyword and a date pattern
            for line in raw_html.splitlines():
                if ("UPDATE" in line.upper() or "PATCH" in line.upper()) and any(d in line for d in all_dates):
                    date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', line)
                    if date_match:
                        latest_date = date_match.group(1).replace('.', '-')
                        break

        # Emergency Fallback: If it's a structural array mapping, the second entry in the array matches tab 2's target
        if not latest_date and len(all_dates) >= 2:
            # Since Lottery is index 0 (2026.02.05), the Update is index 1 (2025.07.28)
            latest_date = all_dates[1].replace('.', '-')
            print(f"Array fallback triggered: {latest_date}")

        if not latest_date:
            print("Error: Could not capture the correct target update timestamp.")
            sys.exit(1)

        print(f"Final Extracted Patch Date: '{latest_date}'")

        # Compare with current file text
        current_saved_date = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                current_saved_date = f.read().strip()
        
        if latest_date != current_saved_date:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(latest_date)
            print(f"Updated {txt_filename}: '{current_saved_date}' -> '{latest_date}'")
        else:
            print(f"File matches live data. No push needed: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_farlight_patch()
