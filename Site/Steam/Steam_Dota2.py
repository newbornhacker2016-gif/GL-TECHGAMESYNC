import os
import re
import requests
from bs4 import BeautifulSoup

# URLs
MAIN_URL = "https://www.dota2.com/patches"

# Adjusted Paths relative to the root directory where the GitHub Action runs
# Saves history in the same folder as the script to keep things clean
HISTORY_FILE = "Site/Steam/Dota2/last_patch.txt" 
# Saves the final text output directly to your target file
OUTPUT_FILE = "Steam/Steam Dota 2.txt"

def get_latest_patch_url():
    response = requests.get(MAIN_URL)
    if response.status_code != 200:
        print("Failed to access Dota 2 patches page")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all('a', href=True)
    patch_urls = []
    for link in links:
        href = link['href']
        if "/patches/7." in href:
            if href.startswith("/"):
                href = f"https://www.dota2.com{href}"
            patch_urls.append(href)
            
    return patch_urls[0] if patch_urls else None

def extract_text_from_patch(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch specific patch notes."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
        
    return soup.get_text(separator="\n", strip=True)

def main():
    # Ensure the target folders exist before trying to save files
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    latest_url = get_latest_patch_url()
    if not latest_url:
        print("No patch URL found.")
        return

    print(f"Current live patch URL: {latest_url}")
    
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()
            
    if latest_url != last_saved_url:
        print("New patch detected! Extracting text...")
        
        with open(HISTORY_FILE, "w") as f:
            f.write(latest_url)
            
        text_output = extract_text_from_patch(latest_url)
        
        # Overwrites or saves the plain text patch notes directly to Steam/Steam Dota 2.txt
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text_output)
            
        print(f"Text-only output saved to {OUTPUT_FILE}")
    else:
        print("No new patch detected since yesterday.")

if __name__ == "__main__":
    main()
