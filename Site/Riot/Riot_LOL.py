import os
import re
import requests
from bs4 import BeautifulSoup

# The raw HTML patch notes tag page
MAIN_URL = "https://www.leagueoflegends.com/en-ph/news/tags/patch-notes/"
HISTORY_FILE = "Site/Riot/last_lol_patch.txt"
OUTPUT_FILE = "LeagueOfLegend.txt"

def get_latest_lol_patch():
    try:
        response = requests.get(MAIN_URL, timeout=15)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Looks for any hyperlink containing "patch" and "notes" in the URL structure
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if "patch" in href.lower() and "notes" in href.lower():
                # Format to absolute link structure
                if href.startswith("/"):
                    href = f"https://www.leagueoflegends.com{href}"
                return href
                
        return None
    except Exception as e:
        print(f"Error scanning page elements: {e}")
        return None

def extract_text_from_patch(url):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code != 200:
            return "Failed to fetch content from the patch article."
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminate code layers, headers, and footers to keep file tidy
        for element in soup(["script", "style", "nav", "footer", "header", "iframe"]):
            element.extract()
            
        return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return f"Error extracting page text content: {e}"

def main():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    latest_url = get_latest_lol_patch()
    if not latest_url:
        print("Could not isolate a valid patch link from the page layout.")
        return

    print(f"Discovered Live Patch URL: {latest_url}")
    
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()
            
    # FORCE WRITE FOR TEST: If you want to force it to populate right now even if it's matching
    if latest_url != last_saved_url or not os.path.exists(OUTPUT_FILE):
        print("Writing fresh patch updates...")
        
        text_output = extract_text_from_patch(latest_url)
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text_output)
            
        with open(HISTORY_FILE, "w") as f:
            f.write(latest_url)
            
        print(f"Successfully compiled text content into {OUTPUT_FILE}")
    else:
        print("The tracked file matches the live page. No new update required.")

if __name__ == "__main__":
    main()
