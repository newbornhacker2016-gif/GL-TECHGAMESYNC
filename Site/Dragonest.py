import os
import re
import sys
import requests
from bs4 import BeautifulSoup

def fetch_dragonnest_patch():
    url = "https://sea.dragonnest.com/news/notice"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Define path to Dragonnest.txt (looks in the parent directory if running from inside /Site)
    # This allows it to work seamlessly locally and on GitHub Actions
    txt_filename = "Dragonnest.txt"
    if not os.path.exists(txt_filename) and os.path.exists(os.path.join("..", txt_filename)):
        txt_path = os.path.join("..", txt_filename)
    else:
        txt_path = txt_filename

    try:
        print(f"Connecting to {url}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('tr')
        latest_completed_date = None

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                category = cells[1].get_text(strip=True).upper()
                title = cells[2].get_text(strip=True)
                
                # Identify explicitly marked UPDATE categories that contain '[Completed]'
                if "UPDATE" in category and "[COMPLETED]" in title.upper():
                    # Strip down string to isolate just the clean date (e.g. "July 7th, 2026")
                    match = re.search(r'\[Completed\]\s*(.*?)\s*Update Patch', title, re.IGNORECASE)
                    if match:
                        latest_completed_date = match.group(1).strip()
                    else:
                        latest_completed_date = title
                    break

        if not latest_completed_date:
            print("Could not find any recent 'UPDATE [Completed]' strings on the webpage.")
            sys.exit(0)

        print(f"Scraped Date from Web: '{latest_completed_date}'")

        # Read current date saved inside Dragonnest.txt to compare
        current_saved_date = ""
        if os.path.exists(txt_path):
            with open(txt_path, "r", encoding="utf-8") as f:
                current_saved_date = f.read().strip()
        
        # Overwrite if data changed or text file is clean
        if latest_completed_date != current_saved_date:
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(latest_completed_date)
            print(f"Updated {txt_filename}: Old value '{current_saved_date}' -> New value '{latest_completed_date}'")
        else:
            print(f"No update required. Already up to date: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_dragonnest_patch()
