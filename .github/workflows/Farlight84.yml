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
        
        # Explicitly isolate and scan the <div class="new-container"> structural element
        container = soup.find('div', class_='new-container')
        
        latest_date = None

        if container:
            print("Successfully located <div class='new-container'> element. Scanning children...")
            # Look inside the container for links or blocks containing update info
            elements = container.find_all(['a', 'li', 'div', 'p', 'span'])
            for el in elements:
                text = el.get_text(" ", strip=True)
                
                # Check if this item is an Update or Patch Note notice
                if "UPDATE" in text.upper() or "PATCH NOTES" in text.upper():
                    # Look for date patterns inside this element (e.g., 2025.07.28 or 2026.02.05)
                    date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', text)
                    if date_match:
                        latest_date = date_match.group(1).replace('.', '-')
                        break
        else:
            print("Warning: <div class='new-container'> was not found directly in static HTML.")
            print("Switching to a deep document scan strategy...")
            # Fallback scan across all elements if structural layout shifted slightly
            for el in soup.find_all(['li', 'a', 'div']):
                text = el.get_text(" ", strip=True)
                if "UPDATE" in text.upper() or "PATCH NOTES" in text.upper():
                    date_match = re.search(r'\b(20\d{2}[\./-]\d{2}[\./-]\d{2})\b', text)
                    if date_match:
                        latest_date = date_match.group(1).replace('.', '-')
                        break

        if not latest_date:
            print("Could not isolate a recent patch update date from the targeted elements.")
            sys.exit(0)

        print(f"Scraped Patch Date from Web: '{latest_date}'")

        # Read the current contents of Farlight84.txt
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
            print(f"No update required. Already synchronized: '{current_saved_date}'")

    except Exception as e:
        print(f"Execution Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fetch_farlight_patch()
