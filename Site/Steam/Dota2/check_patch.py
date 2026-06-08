import os
import re
import requests
from bs4 import BeautifulSoup

# URLs
MAIN_URL = "https://www.dota2.com/patches"
HISTORY_FILE = "last_patch.txt"
OUTPUT_FILE = "latest_patch_notes.txt"

def get_latest_patch_url():
    response = requests.get(MAIN_URL)
    if response.status_code != 200:
        print("Failed to access Dota 2 patches page")
        return None
    
    # Use BeautifulSoup to find patch links
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Look for links containing "/patches/7."
    links = soup.find_all('a', href=True)
    patch_urls = []
    for link in links:
        href = link['href']
        if "/patches/7." in href:
            # Ensure it's an absolute URL
            if href.startswith("/"):
                href = f"https://www.dota2.com{href}"
            patch_urls.append(href)
            
    return patch_urls[0] if patch_urls else None

def extract_text_from_patch(url):
    response = requests.get(url)
    if response.status_code != 200:
        return "Failed to fetch specific patch notes."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Strips out HTML elements like scripts/styles and leaves just raw text
    for script in soup(["script", "style"]):
        script.extract()
        
    return soup.get_text(separator="\n", strip=True)

def main():
    latest_url = get_latest_patch_url()
    if not latest_url:
        print("No patch URL found.")
        return

    print(f"Current live patch URL: {latest_url}")
    
    # Read what the patch was yesterday
    last_saved_url = ""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            last_saved_url = f.read().strip()
            
    # If the URL changed (e.g., from 7.41c to 7.41d)
    if latest_url != last_saved_url:
        print("New patch detected! Extracting text...")
        
        # Save the new URL so we don't repeat tomorrow
        with open(HISTORY_FILE, "w") as f:
            f.write(latest_url)
            
        # Get only the text content of the new patch page
        text_output = extract_text_from_patch(latest_url)
        
        # Write the text-only output to a file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(text_output)
            
        print(f"Text-only output saved to {OUTPUT_FILE}")
    else:
        print("No new patch detected since yesterday.")

if __name__ == "__main__":
    main()
